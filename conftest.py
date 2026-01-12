import pytest
from playwright.sync_api import Page

from adapter.selfheal.page_proxy import HealingPage
from adapter.selfheal.self_healer import SimpleSelfHealer
import logging
from logging_config import setup_logging
from test_context import current_test


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    current_test.set(item.nodeid)


def pytest_configure():
    setup_logging(level=logging.INFO)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict):
    return {**browser_context_args, "locale": "en-US"}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict):
    return {**browser_type_launch_args, "headless": False}


@pytest.fixture
def healer(page: Page):
    healer = SimpleSelfHealer()
    return HealingPage(page, healer)


# @pytest.fixture
# def page():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context()
#         page = context.new_page()
#         yield page
#         context.close()
#         browser.close()

# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_call(item):
#         outcome = yield
#         error = outcome.exception
#         if error:
#             page = item.funcargs.get("page")

#             ctx = normalize_failure(
#                 tool="playwright",
#                 page=page,
#                 exception=error,
#                 test_name=item.name,
#                 test_type="REGRESSION",
#             )
#             result = handle_failure(ctx)
#             print(result)
#             apply_healed_locator(
#                 page,
#                 healed_locator=result['healed_locator'],
#                 action="click"
#             )
#             outcome.force_result(None)
#             return
#         raise
