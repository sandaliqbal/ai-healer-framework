from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum
from playwright.sync_api import Page

from adapter.selfheal.models import ErrorInfo, LocatorDescriptor


class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    TRANSFORM = "TRANSFORM"
    ESCALATE = "ESCALATE"
    NOOP = "NOOP"


@dataclass
class Rule:
    id: str
    when: Dict[str, Any]
    match: Dict[str, Any]
    action: Dict[str, Any]
    confidence: Dict[str, Any]
    explain: str
    priority: int = 0


@dataclass
class Artifact:
    dom_snapshot: str
    a11y_snapshot: str
    screenshot: str


@dataclass
class Failure:
    id: str
    type: str
    error: ErrorInfo
    original_locator: LocatorDescriptor


@dataclass
class FailureContext:
    tool: str
    page: Page
    test_type: str
    test_name: str
    environment: str
    failure: Failure
    artifacts: Artifact
    component: Optional[str] = field(default=None)
