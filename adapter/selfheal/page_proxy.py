from playwright.sync_api import Page

from adapter.selfheal.healer_interface import ILocatorHealer
from adapter.selfheal.locator_proxy import HealingLocatorProxy


class HealingPage:
    def __init__(self, page: Page, healer: ILocatorHealer):
        self._page = page
        self._healer = healer

    # --- Pass-through for everything else ---

    def goto(self, url: str, **kwargs):
        return self._page.goto(url, **kwargs)

    def __getattr__(self, name):
        attr = getattr(self._page, name)
        if name.startswith("get_by_") or name == "locator":

            def wrapper(*args, **kwargs):
                loc = attr(*args, **kwargs)
                return HealingLocatorProxy(loc, self._healer)

            return wrapper
        return attr
