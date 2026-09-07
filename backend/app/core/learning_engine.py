"""
Self Learning Engine for ConsciousCore V1.
Processes experience, extracts lessons, updates knowledge, and adapts procedures.
"""

from typing import Dict, Any, List
import time

class LearningEngine:
    def __init__(self):
        self.lessons: List[Dict[str, Any]] = [
            {
                "id": "les_001",
                "category": "procedure",
                "source": "experience",
                "lesson": "FTS5 search outperforms fuzzy matching for technical system queries",
                "confidence": 0.95,
                "created_at": time.time()
            }
        ]

    def record_experience(self, action: str, outcome: str, success: bool, details: Dict[str, Any] = None) -> Dict[str, Any]:
        lesson_text = f"Action '{action}' resulted in '{outcome}' (Success={success})"
        lesson = {
            "id": f"les_{len(self.lessons) + 1:03d}",
            "category": "failure_adaptation" if not success else "success_pattern",
            "source": "runtime_experience",
            "lesson": lesson_text,
            "confidence": 0.9 if success else 0.8,
            "details": details or {},
            "created_at": time.time()
        }
        self.lessons.append(lesson)
        return lesson

    def get_lessons(self) -> List[Dict[str, Any]]:
        return self.lessons
