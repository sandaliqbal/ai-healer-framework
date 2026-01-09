from playwright.sync_api import Page, Locator
from adapter.selfheal.models import LocatorDescriptor, ValidationResult
from adapter.selfheal.retry import build_locator


def validate_locator_uniqueness(
    page: Page, locator_exp: LocatorDescriptor, timeout: int = 2000
) -> ValidationResult:
    """
    Executes a Playwright locator expression and validates uniqueness.
    """

    try:
        # Evaluate locator expression safely
        locator: Locator = build_locator(page, locator_exp)

        # Wait briefly for DOM stability
        locator.first.wait_for(timeout=timeout)

        count = locator.count()

        return ValidationResult(
            locator=locator_exp,
            locator_rank=locator_exp.rank,
            count=count,
            is_unique=(count == 1),
            error=None,
        )

    except Exception as e:
        return ValidationResult(
            locator=locator_exp,
            locator_rank=locator_exp.rank,
            count=0,
            is_unique=False,
            error=str(e),
        )
