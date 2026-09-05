from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class ActionPermission:
    action: str
    allowed: bool
    requires_approval: bool
    reason: str

class SafetyEngine:
    def __init__(self, autonomy_level: int = 1):
        self.autonomy_level = max(0, min(3, autonomy_level))
        self.blocked = {"auth_bypass", "secret_extraction", "credential_capture", "mfa_bypass", "captcha_bypass", "destructive_system_change"}

    def evaluate(self, action: str, risk: float = .5) -> ActionPermission:
        risk = max(0, min(1, risk))
        if action in self.blocked:
            return ActionPermission(action, False, False, "action is prohibited by safety policy")
        approval = self.autonomy_level < 2 or risk >= .5
        return ActionPermission(action, True, approval, "explicit approval required before external or risky action" if approval else "allowed within configured autonomy")

    def snapshot(self):
        return {"autonomy_level": self.autonomy_level, "blocked_actions": sorted(self.blocked), "external_actions_require_approval": self.autonomy_level < 2}
