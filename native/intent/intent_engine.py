"""
Native Intent Engine for ConsciousCore V1.
Supports intent resolution across English, Urdu, and Roman Urdu.
"""

import re
from typing import Dict, Any

class NativeIntentEngine:
    def __init__(self):
        self.mappings = {
            "self_capabilities": [
                r"apne skills dikhao",
                r"show your skills",
                r"tum kya kya kar sakte ho",
                r"what can you do",
                r"show capabilities"
            ],
            "check_myself": [
                r"check myself",
                r"apne aap ko check karo",
                r"system check",
                r"run diagnostics"
            ],
            "system_status": [
                r"system status",
                r"status kya hai",
                r"show health"
            ]
        }

    def detect_intent(self, user_text: str) -> Dict[str, Any]:
        text_clean = user_text.strip().lower()
        for intent, patterns in self.mappings.items():
            for pat in patterns:
                if re.search(pat, text_clean):
                    return {
                        "intent": intent,
                        "confidence": 0.95,
                        "matched_pattern": pat,
                        "language_detected": "roman_urdu" if "kya" in text_clean or "karo" in text_clean else "english"
                    }
        return {
            "intent": "general_query",
            "confidence": 0.5,
            "matched_pattern": None,
            "language_detected": "english"
        }
