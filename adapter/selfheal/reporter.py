from typing import Optional
from adapter.selfheal.models import (
    LocatorDescriptor,
    ErrorInfo,
)
from adapter.selfheal.collector import collect_dom, collect_a11y, collect_screenshot
from rule_engine.models import Artifact, Failure, FailureContext
import uuid
import re

WAITING_FOR_RE = re.compile(
    r"waiting for\s+"
    r"(?:page\.)?"
    r"(?P<strategy>get_by_[a-z_]+|locator)"
    r"\("
    r"(?P<args>.*)"
    r"\)",
    re.IGNORECASE,
)

LOCATOR_PATTERNS = {
    "role": re.compile(
        r"""
    page\.get_by_role\(
        \s*
        (?P<quote>["'])
        (?P<role>[^"']+)
        (?P=quote)
        \s*,\s*
        name\s*=\s*
        (?P<quote2>["'])
        (?P<name>[^"']+)
        (?P=quote2)
        (?P<options>.*)
        \s*
    \)
    """,
        re.VERBOSE,
    ),
    "text": re.compile(
        r"page\.get_by_text\(\s*"
        r'(?P<quote>[\'"])'
        r"(?P<value>.*?)"
        r"(?P=quote)"
        r"(?P<options>.*)"
        r"\s*\)"
    ),
    "label": re.compile(r"page\.get_by_label\(\s*\'(?P<value>[^\']+)\'\s*\)"),
    "placeholder": re.compile(
        r"page\.get_by_placeholder\(\s*\'(?P<value>[^\']+)\'\s*\)"
    ),
    "test_id": re.compile(r"page\.get_by_test_id\(\s*\'(?P<value>[^\']+)\'\s*\)"),
    "locator": re.compile(r"page\.locator\(\s*\'(?P<value>.+?)\'\s*\)"),
}

XPATH_PATTERNS = [
    r"^/{1,2}",  # / or //
    r"@[\w:-]+",  # @id, @class, @data-test
    r"\[.*?\]",  # predicates [...]
    r"text\(\)",  # text()
    r"contains\(",  # contains()
]

CSS_PATTERNS = [
    r"#[\w-]+",  # #id
    r"\.[\w-]+",  # .class
    r"\[[\w-]+(=.*?)?\]",  # [attr] or [attr=value]
    r":[\w-]+(\(.*?\))?",  # :nth-child(), :not()
    r"^[a-zA-Z][\w-]*$",  # tag only (button)
    r"^[a-zA-Z][\w-]*[.#]",  # tag.class or tag#id
    r"\s+[>+~]?\s*[\w.#\[]+",  # combinators
]

STRATEGY_MAP = {
    "get_by_text": "text",
    "get_by_label": "label",
    "get_by_placeholder": "placeholder",
    "get_by_role": "role",
    "locator": "css",
}


def normalize_failure(
    *,
    tool: str,
    page,
    exception: Exception,
    test_name: str,
    test_type: str,
    environment: str = "QA",
    run_id: str = "local",
) -> FailureContext:
    """
    Convert raw test failure into canonical FailureContext
    """
    if isinstance(exception, AssertionError):
        error = ErrorInfo(type="AssertionError", subtype=None, message=str(exception))
    else:
        error = ErrorInfo(type=exception.name, subtype=None, message=exception.message)
    failure_type = classify_failure(error)
    original_locator: LocatorDescriptor = parse_playwright_error(exception.message)
    failure = Failure(
        str(uuid.uuid4()),
        failure_type,
        error,
        original_locator,
    )
    ctx = FailureContext(
        tool=tool,
        page=page,
        test_type=test_type,
        test_name=test_name,
        environment=environment,
        failure=failure,
        artifacts=Artifact(
            collect_dom(page, failure.id),
            collect_a11y(page, failure.id),
            collect_screenshot(page, failure.id),
        ),
    )

    return ctx


def classify_failure(error: ErrorInfo) -> str:
    WAITING_FOR_LOCATOR_RE = re.compile(
        r"waiting for (locator\()?(page\.)?(get_by_[a-z_]+|locator)\(.*?\)\)?",
        re.IGNORECASE,
    )
    if "TimeoutError" in error.type:
        if bool(WAITING_FOR_LOCATOR_RE.search(error.message)):
            return "LOCATOR_NOT_FOUND"
        if 'waiting until "load"' in error.message:
            return "PAGE_LOAD_TIMEOUT"

    if "strict mode violation" in error.message.lower():
        return "STRICT_MODE_VIOLATION"

    if "AssertionError" in error.type:
        return "ASSERTION_FAILURE"

    if "net::ERR" in error.message:
        return "NETWORK_FAILURE"

    return "UNKNOWN_FAILURE"


def parse_playwright_error(message: str) -> Optional[LocatorDescriptor]:
    """
    Extract locator strategy and primary value from Playwright timeout message.
    """
    match = WAITING_FOR_RE.search(message)
    if not match:
        return None

    raw_strategy = match.group("strategy")
    args = match.group("args").strip()
    s = normalize(args)
    loc = "page." + raw_strategy + "(" + s + ")"
    pl_loc = parse_playwright_locator(loc)
    return pl_loc


def normalize(s: str) -> str:
    s = s.strip()
    s = s.replace('"', "'")
    return s


def infer_locator_strategy(selector: str):
    selector = selector.strip()

    if selector.startswith("/") or selector.startswith("("):
        return "xpath"

    if selector.startswith("#") or selector.startswith(".") or "[" in selector:
        return "css"

    return "css"


def parse_playwright_locator(code: str) -> LocatorDescriptor:
    code = code.strip()

    # Role
    if m := LOCATOR_PATTERNS["role"].match(code):
        return LocatorDescriptor(
            strategy="role",
            role=m.group("role"),
            name=m.group("name") if m.group("name") else "",
            value=m.group("name") if m.group("name") else "",
            options=m.group("options"),
        )

    # Text
    if m := LOCATOR_PATTERNS["text"].match(code):
        return LocatorDescriptor(strategy="text", value=m.group("value"))

    # Label
    if m := LOCATOR_PATTERNS["label"].match(code):
        return LocatorDescriptor(strategy="label", value=m.group("value"))

    # Placeholder
    if m := LOCATOR_PATTERNS["placeholder"].match(code):
        return LocatorDescriptor(strategy="placeholder", value=m.group("value"))

    # Test ID
    if m := LOCATOR_PATTERNS["test_id"].match(code):
        return LocatorDescriptor(strategy="test_id", value=m.group("value"))

    # page.locator(...)
    if m := LOCATOR_PATTERNS["locator"].match(code):
        selector = m.group("value")
        strategy = infer_locator_strategy(selector)

        return LocatorDescriptor(strategy=strategy, value=selector)

    raise ValueError(f"Unsupported Playwright locator syntax: {code}")


def is_xpath(s: str) -> bool:
    return (
        s.startswith("/")
        or s.startswith("./")
        or s.startswith("(")
        or "::" in s
        or s.startswith("xpath=")
    )


def is_css_selector(s: str) -> bool:
    # Hard reject XPath signals
    if s.startswith(("/", ".//")) or "@" in s or "text()" in s:
        return False

    for pattern in CSS_PATTERNS:
        if re.search(pattern, s):
            return True

    return False
