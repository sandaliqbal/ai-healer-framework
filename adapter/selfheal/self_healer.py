from adapter.selfheal.healer_interface import ILocatorHealer
from adapter.selfheal.models import LocatorDescriptor
from adapter.selfheal.orchestrator import manage_failure
from adapter.selfheal.reporter import normalize_failure
from playwright.sync_api import Locator
from adapter.selfheal.retry import build_locator
import logging

logger = logging.getLogger(__name__)


class SimpleSelfHealer(ILocatorHealer):
    def heal(self, *, page, exception) -> Locator:
        ctx = normalize_failure(
            tool="playwright",
            page=page,
            exception=exception,
            test_name="login",
            test_type="REGRESSION",
        )

        result = manage_failure(ctx)
        logger.info(f"Healing engine result: {result}")
        if result["decision"] == "ALLOW":
            loc: LocatorDescriptor = result["healed_locator"]
            if loc.rank >= 100 or loc.confidence >= 0.9:
                healed_locator: Locator = build_locator(page, result["healed_locator"])
                logger.info(f"Returning healed locator {healed_locator}")
                return healed_locator
            else:
                logger.info(
                    f"Manual Review required as locator score doesn't "
                    f"meet the required threshold. "
                    f"Suggested locator {loc.to_playwright()}."
                    f"Locator rank: {loc.rank}, Locator confidence: {loc.confidence}."
                )
                raise exception
        else:
            raise exception
