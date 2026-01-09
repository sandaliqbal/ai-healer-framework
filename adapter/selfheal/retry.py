from adapter.selfheal.models import LocatorDescriptor
from playwright.sync_api import Page, Locator


def build_locator(page: Page, d: LocatorDescriptor) -> Locator:
    if d.strategy == "role":
        return page.get_by_role(
            d.role, name=d.value, exact=d.exact if hasattr(d, "exact") else False
        )

    if d.strategy == "text":
        return page.get_by_text(
            d.value, exact=d.exact if hasattr(d, "exact") else False
        )

    if d.strategy == "label":
        return page.get_by_label(d.value)

    if d.strategy == "placeholder":
        return page.get_by_placeholder(d.value)

    if d.strategy == "xpath":
        return page.locator(d.value)

    if d.strategy == "css":
        return page.locator(d.value)

    raise ValueError(f"Unsupported locator strategy: {d.strategy}")
