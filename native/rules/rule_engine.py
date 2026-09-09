"""
Native Rule Engine for ConsciousCore V1.
Evaluates conditions (AND, OR, NOT, >, <, >=, <=, ==, contains, matches, in) against runtime state.
"""

from typing import Dict, Any, List

class NativeRuleEngine:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = [
            {
                "rule_id": "ram.high",
                "condition": {"ram_usage": {"operator": ">", "value": 90}},
                "action": {"type": "pause_idle_ai"},
                "priority": 100,
                "enabled": True
            },
            {
                "rule_id": "battery.low",
                "condition": {"battery": {"operator": "<", "value": 20}},
                "action": {"type": "pause_learning"},
                "priority": 90,
                "enabled": True
            }
        ]

    def _eval_condition(self, field_val: Any, op: str, target_val: Any) -> bool:
        if op == ">": return field_val > target_val
        if op == "<": return field_val < target_val
        if op == ">=": return field_val >= target_val
        if op == "<=": return field_val <= target_val
        if op == "==": return field_val == target_val
        if op == "contains": return target_val in field_val
        if op == "in": return field_val in target_val
        return False

    def evaluate(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        triggered_actions = []
        for rule in self.rules:
            if not rule.get("enabled"): continue
            conds = rule.get("condition", {})
            rule_passed = True
            for field, spec in conds.items():
                val = state.get(field)
                if val is None or not self._eval_condition(val, spec.get("operator", "=="), spec.get("value")):
                    rule_passed = False
                    break
            if rule_passed:
                triggered_actions.append(rule.get("action"))
        return triggered_actions
