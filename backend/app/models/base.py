from __future__ import annotations
from abc import ABC, abstractmethod

class LocalModel(ABC):
    name = "local-model"
    backend = "unknown"

    @abstractmethod
    async def generate(self, prompt: str, context: list[str] | None = None) -> str:
        raise NotImplementedError

    def info(self) -> dict:
        return {"name": self.name, "backend": self.backend, "local_only": True}
