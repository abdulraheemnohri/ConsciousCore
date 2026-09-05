from __future__ import annotations
from dataclasses import dataclass, asdict
from .safety import SafetyEngine

@dataclass
class Tool:
    name: str
    description: str
    risk: float = .5
    enabled: bool = True

class ToolRegistry:
    def __init__(self, safety: SafetyEngine):
        self.safety = safety
        self.tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, risk: float = .5):
        tool = Tool(name, description, max(0, min(1, risk)))
        self.tools[name] = tool
        return asdict(tool)

    def authorize(self, name: str):
        tool = self.tools.get(name)
        if not tool or not tool.enabled:
            return {"allowed": False, "reason": "tool unavailable"}
        return asdict(self.safety.evaluate(name, tool.risk))

    def snapshot(self):
        return [asdict(x) for x in self.tools.values()]
