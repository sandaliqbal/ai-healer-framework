def calculate_confidence(action: str, source: str | None = None) -> float:
    if source == "RULE_ENGINE":
        return 0.95

    if source == "LLM" and action == "UPDATE_LOCATOR":
        return 0.75

    if action == "FLAG_FOR_REVIEW":
        return 0.2

    return 0.3
