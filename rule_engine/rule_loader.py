import yaml
from typing import List
from pathlib import Path

from rule_engine.models import Rule, DecisionType

def load_rules_from_yaml(path: str) -> List[Rule]:
    yaml_path = Path(path)

    if not yaml_path.exists():
        raise FileNotFoundError(f"Rule file not found: {path}")

    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validate_root(data)

    rules: List[Rule] = []

    for policy in data.get("policies", []):
        for rule_def in policy.get("rules", []):
            rules.append(parse_rule(rule_def))

    return rules

def validate_root(data: dict):
    if not isinstance(data, dict):
        raise ValueError("Rules YAML must be a dictionary")

    if "policies" not in data:
        raise ValueError("Rules YAML must contain 'policies'")

REQUIRED_FIELDS = {"id", "when", "match", "action", "confidence", "explain"}

def parse_rule(rule_def: dict) -> Rule:
    missing = REQUIRED_FIELDS - rule_def.keys()
    if missing:
        raise ValueError(
            f"Rule '{rule_def.get('id', '<unknown>')}' missing fields: {missing}"
        )

    action_type = rule_def["action"]["type"]

    if action_type not in DecisionType.__members__:
        raise ValueError(f"Invalid action type: {action_type}")

    return Rule(
        id=rule_def["id"],
        when=rule_def["when"],
        match=rule_def["match"],
        action=rule_def["action"],
        confidence=rule_def["confidence"],
        explain=rule_def["explain"],
        priority=rule_def.get("priority", 0),
    )
