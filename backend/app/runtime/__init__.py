"""Universal runtime routing for local, cloud, remote, hybrid and parallel cognition."""
from .types import RuntimeMode, RuntimeRequest, RuntimeResult
from .router import RuntimeRouter

__all__ = ["RuntimeMode", "RuntimeRequest", "RuntimeResult", "RuntimeRouter"]
