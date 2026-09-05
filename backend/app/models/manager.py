from __future__ import annotations
from pathlib import Path
from .llama_cpp_adapter import LlamaCppModel

class ModelManager:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.models: dict[str, LlamaCppModel] = {}
        self.active: str | None = None

    def register_gguf(self, model_id: str, path: str, **kwargs):
        model = LlamaCppModel(path, name=model_id, **kwargs)
        self.models[model_id] = model
        if self.active is None:
            self.active = model_id
        return model.info()

    def discover_gguf(self):
        self.model_dir.mkdir(parents=True, exist_ok=True)
        discovered = []
        for path in sorted(self.model_dir.glob("*.gguf")):
            model_id = path.stem
            if model_id not in self.models:
                self.register_gguf(model_id, str(path))
                discovered.append(model_id)
        return discovered

    def list(self):
        return {"active": self.active, "models": [m.info() for m in self.models.values()]}

    def get_active(self):
        return self.models.get(self.active) if self.active else None

    def activate(self, model_id: str):
        if model_id not in self.models:
            raise KeyError(model_id)
        self.active = model_id
        return self.models[model_id].info()
