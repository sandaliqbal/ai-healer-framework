from adapter.selfheal.page_proxy import HealingPage
import logging

logger = logging.getLogger(__name__)


def test_login_no_healing(healer: HealingPage):
    """ Test which passes and requires no healing """
    healer.goto("https://www.facebook.com/")
    healer.get_by_role("button", name="Log in", exact=True).click()


def test_login_with_healing(healer: HealingPage):
    """ Test which requires healing. Healing is applied based on locatore score """
    healer.goto("https://www.facebook.com/")
    healer.locator("//button[.//text()[normalize-space()='Log']]").click()
    logger.info("applied healing successfully")