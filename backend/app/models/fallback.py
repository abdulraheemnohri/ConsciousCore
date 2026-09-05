from __future__ import annotations
from .base import LocalModel

class FallbackModel(LocalModel):
    name = "ConsciousCore-Fallback"
    backend = "deterministic"

    async def generate(self, prompt: str, context: list[str] | None = None) -> str:
        prefix = f"Relevant memory: {context[0]}\n\n" if context else ""
        return prefix + "ConsciousCore received: " + prompt
