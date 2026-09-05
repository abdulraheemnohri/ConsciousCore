from __future__ import annotations
from pathlib import Path
from .llama_cpp_adapter import LlamaCppModel

class ModelManager:
    def __init__(self):
        self.models: dict[str, LlamaCppModel] = {}
        self.active: str | None = None

    def register_gguf(self, model_id: str, path: str, **kwargs):
        model = LlamaCppModel(path, name=model_id, **kwargs)
        self.models[model_id] = model
        if self.active is None:
            self.active = model_id
        return model.info()

    def list(self):
        return {"active": self.active, "models": [m.info() for m in self.models.values()]}

    def get_active(self):
        return self.models.get(self.active) if self.active else None

    def activate(self, model_id: str):
        if model_id not in self.models:
            raise KeyError(model_id)
        self.active = model_id
        return self.models[model_id].info()
