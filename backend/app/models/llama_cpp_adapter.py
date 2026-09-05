from __future__ import annotations
import asyncio
from pathlib import Path
from .base import LocalModel

class LlamaCppModel(LocalModel):
    backend = "llama.cpp"

    def __init__(self, model_path: str, name: str | None = None, **kwargs):
        self.model_path = Path(model_path)
        self.name = name or self.model_path.name
        self.kwargs = kwargs
        self._llm = None

    def _load(self):
        if self._llm is not None:
            return self._llm
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError("llama-cpp-python is not installed. Install it to enable GGUF inference.") from exc
        if not self.model_path.exists():
            raise FileNotFoundError(f"GGUF model not found: {self.model_path}")
        self._llm = Llama(model_path=str(self.model_path), **self.kwargs)
        return self._llm

    def _generate_sync(self, full_prompt: str) -> str:
        llm = self._load()
        result = llm(full_prompt, max_tokens=512, temperature=0.2)
        return result["choices"][0]["text"].strip()

    async def generate(self, prompt: str, context: list[str] | None = None) -> str:
        memories = "\n".join(f"- {x}" for x in (context or []))
        full_prompt = f"Relevant memory:\n{memories}\n\nUser:\n{prompt}" if memories else prompt
        return await asyncio.to_thread(self._generate_sync, full_prompt)

    def info(self):
        return {**super().info(), "model_path": str(self.model_path), "loaded": self._llm is not None}
