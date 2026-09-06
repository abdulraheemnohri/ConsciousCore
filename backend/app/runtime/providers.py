from __future__ import annotations

from typing import Any, Protocol


class ModelProvider(Protocol):
    name: str

    async def generate(self, prompt: str, **kwargs: Any) -> str: ...
    async def health_check(self) -> dict[str, Any]: ...
    def metadata(self) -> dict[str, Any]: ...


class ProviderRegistry:
    """Runtime-neutral registry for local, cloud and self-hosted model adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}

    def register(self, provider: ModelProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> ModelProvider | None:
        return self._providers.get(name)

    def list(self) -> list[dict[str, Any]]:
        return [provider.metadata() for provider in self._providers.values()]
