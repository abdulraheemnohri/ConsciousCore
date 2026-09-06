import pytest
from app.runtime.provider_manager import ProviderManager

@pytest.mark.asyncio
async def test_unknown_provider_health_is_safe():
    result=await ProviderManager().health("missing")
    assert result["ok"] is False
    assert result["error"] == "provider_not_configured"

def test_provider_registration_does_not_expose_api_key():
    manager=ProviderManager(); manager.register("remote","http://127.0.0.1:11434","model","secret")
    assert "api_key" not in str(manager.snapshot())
