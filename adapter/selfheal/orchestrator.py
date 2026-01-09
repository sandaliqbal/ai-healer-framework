from typing import List, Dict
from adapter.selfheal.reporter import parse_playwright_locator
from adapter.selfheal.score_engine import rank_locators
from analyzer.llm_analyzer import analyze_with_llm
from rule_engine.models import FailureContext, Rule
from rule_engine.rule_loader import load_rules_from_yaml
from rule_engine.execution_engine import ExecutionEngine
from adapter.selfheal.locator_transformer import LocatorTransformer
from adapter.selfheal.snapshot_helper import load_snapshot
from adapter.selfheal.models import LocatorDescriptor, ValidationResult
from adapter.selfheal.validator import validate_locator_uniqueness
import logging

logger = logging.getLogger(__name__)

rules = load_rules_from_yaml("rule_engine/rules.yaml")
engine = ExecutionEngine(rules)


def get_rule_decision(context: FailureContext) -> Rule:
    rule_decision: Rule = engine.evaluate(context)
    logger.info(rule_decision)
    return rule_decision


def manage_failure(context: FailureContext) -> Dict:
    rule_decision = get_rule_decision(context)
    if rule_decision["decision"] == "ALLOW":
        return get_locator(context, rule_decision)
    else:
        return rule_decision


def get_locator(context: FailureContext, rule_decision: Rule) -> Dict:
    candidates = get_candidate_locators(context, rule_decision)
    ranked_locators = rank_locators(candidates)
    results: List[ValidationResult] = [
        validate_locator_uniqueness(context.page, locator)
        for locator in ranked_locators
    ]
    final_result = {}
    for result in results:
        if result.is_unique:
            final_result["failure"] = context.failure.type
            final_result["original_locator"] = (
                context.failure.original_locator.to_playwright()
            )
            final_result["healed_locator"] = result.locator
            final_result["locator_rank"] = result.locator.rank
            final_result["decision"] = rule_decision["decision"]
        return final_result
    return final_result


def get_candidate_locators(context: FailureContext, rule_decision):
    locators: list[LocatorDescriptor] = []
    if rule_decision["decision"] != "DENY":
        snap = load_snapshot(context.artifacts.a11y_snapshot)
        transformer = LocatorTransformer()
        locators = transformer.transform(
            original=context.failure.original_locator, snapshot=snap
        )
        if not locators:
            locators = []
            logger.info(
                "No locators found from deterministic search. Calling LLM now...."
            )
            llm_response = analyze_with_llm(
                context.artifacts.a11y_snapshot,
                context.failure.original_locator.to_playwright(),
            )
            for text in llm_response:
                parsed: LocatorDescriptor = parse_playwright_locator(text["locator"])
                parsed.confidence = text["confidence"]
                locators.append(parsed)
            logger.info(f"List of locators fetched through LLM {locators}")
        return locators
