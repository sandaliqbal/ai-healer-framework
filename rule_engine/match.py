from typing import Dict, Any
from rule_engine.models import Rule, FailureContext

def match_when(when: Dict[str, Any], ctx: FailureContext) -> bool:
    for key, expected in when.items():
        actual = getattr(ctx, key, None)

        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif isinstance(expected, str):
            if expected != actual:
                return False
        else:
            return False

    return True

def match_failure(match: Dict[str, Any], ctx: FailureContext) -> bool:
    failure = ctx.failure

    for key, expected in match.items():
        # failure_type
        if key == "failure_type":
            if failure.type != expected:
                return False

        # error_contains
        elif key == "error_contains":
            error = failure.error
            if isinstance(expected, list):
                if not any(e in error for e in expected):
                    return False
            elif expected not in error:
                return False

        # locator_contains
        elif key == "locator_contains":
            locator = failure.original_locator
            if expected not in locator:
                return False

        # attempts_exhausted
        elif key == "attempts_exhausted":
            if expected and ctx.attempt < 2:
                return False

        # artifact existence
        elif key == "requires":
            for artifact in expected:
                if not ctx.artifacts.get(artifact, False):
                    return False

        else:
            return False

    return True

def build_decision(rule: Rule) -> Dict[str, Any]:
    return {
        "decision": rule.action["type"],
        "rule_id": rule.id,
        "confidence": rule.confidence.get("score", 0.0),
        "details": rule.action.get("transform"),
        "explain": rule.explain
    }

