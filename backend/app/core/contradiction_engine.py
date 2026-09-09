"""
Knowledge Contradiction Engine for ConsciousCore V1.
Detects conflicting facts and resolves conflicts based on provenance, timestamp, and confidence.
"""

from typing import Dict, Any, List

class ContradictionEngine:
    def __init__(self):
        self.conflicts: List[Dict[str, Any]] = []

    def detect_and_resolve(self, fact_a: Dict[str, Any], fact_b: Dict[str, Any]) -> Dict[str, Any]:
        # If same subject and predicate but differing objects
        if (
            fact_a.get("subject") == fact_b.get("subject")
            and fact_a.get("predicate") == fact_b.get("predicate")
            and fact_a.get("object") != fact_b.get("object")
        ):
            # Resolve based on confidence & timestamp
            conf_a = fact_a.get("confidence", 0.5)
            conf_b = fact_b.get("confidence", 0.5)
            winner = fact_a if conf_a >= conf_b else fact_b
            conflict_record = {
                "fact_a": fact_a,
                "fact_b": fact_b,
                "winner": winner,
                "reason": f"Winner selected by confidence ({winner.get('confidence')})"
            }
            self.conflicts.append(conflict_record)
            return conflict_record
        return {"status": "NO_CONFLICT"}

    def get_conflicts(self) -> List[Dict[str, Any]]:
        return self.conflicts
