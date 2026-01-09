from playwright.sync_api import Locator
from adapter.selfheal.healer_interface import ILocatorHealer


class HealingLocatorProxy:
    def __init__(self, locator: Locator, healer: ILocatorHealer):
        self._locator = locator
        self._page = locator.page
        self._healer = healer

    def click(self, **kwargs):
        self._page.get_by_alt_text
        self._page.get_by_label
        self._page.get_by_placeholder
        self._page.get_by_role
        self._page.get_by_test_id
        self._page.get_by_text
        self._page.get_by_title
        return self._execute("click", **kwargs)

    def fill(self, value, **kwargs):
        return self._execute("fill", value, **kwargs)

    def _execute(self, action, *args, **kwargs):
        try:
            return getattr(self._locator, action)(*args, **kwargs)
        except Exception as e:
            healed = self._healer.heal(
                page=self._page,
                exception=e,
            )
            return getattr(healed, action)(*args, **kwargs)
