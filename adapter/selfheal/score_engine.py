from adapter.selfheal.models import LocatorDescriptor


BASE_WEIGHTS = {
    "role": 100,
    "label": 95,
    "placeholder": 90,
    "text": 70,
    "css": 40,
    "xpath": 20,
}

ROLE_PRIORITY = {
    "button": 30,
    "combobox": 25,
    "textbox": 25,
    "checkbox": 20,
    "radio": 20,
    "link": 15,
}

LANDMARK_PRIORITY = {
    "main": 30,  # primary content → best
    "search": 25,  # forms / search boxes
    "navigation": 15,  # menus
    "banner": 5,  # header
    "contentinfo": -20,  # footer → usually duplicated
}


def score_locator(locator: LocatorDescriptor) -> float:
    score = BASE_WEIGHTS.get(locator.strategy, 10)

    # Landmark-aware scoring
    score += score_landmark(locator)
    score += score_role(locator)
    locator.rank = round(score, 2)
    return round(score, 2)


def score_landmark(locator: LocatorDescriptor) -> int:
    if not locator.landmark:
        return 0
    return LANDMARK_PRIORITY.get(locator.landmark, 0)


def score_role(locator: LocatorDescriptor) -> int:
    if not locator.value:
        return 0
    return ROLE_PRIORITY.get(locator.value, 0)


def rank_locators(locators: list[LocatorDescriptor]) -> list[LocatorDescriptor]:
    return sorted(locators, key=score_locator, reverse=True)
