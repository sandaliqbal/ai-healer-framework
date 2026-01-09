from typing import List, Dict, Any
from rule_engine.models import Rule, DecisionType, FailureContext
from rule_engine.match import match_failure, match_when, build_decision


class ExecutionEngine:

    def __init__(self, rules: List[Rule]):
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    def evaluate(self, ctx: FailureContext) -> Dict[str, Any]:
        for rule in self.rules:
            if not match_when(rule.when, ctx):
                continue

            if match_failure(rule.match, ctx):
                return build_decision(rule)

        return self.default_noop()

    @staticmethod
    def default_noop() -> Dict[str, Any]:
        return {
            "decision": DecisionType.NOOP.value,
            "confidence": 0.0,
            "explain": "No matching rule found",
        }
