from fastapi import APIRouter
from pydantic import BaseModel

class SettingsUpdate(BaseModel):
    changes:dict

def create_router(engine):
    router=APIRouter(prefix="/api/settings/v2",tags=["Settings V2"])
    @router.get("")
    async def get_settings(): return engine.settings_v2.snapshot()
    @router.patch("")
    async def update_settings(body:SettingsUpdate):
        result=engine.settings_v2.update(body.changes)
        engine.safety.autonomy_level=result["autonomy_level"]
        return result
    @router.post("/reset")
    async def reset_settings():
        result=engine.settings_v2.reset(); engine.safety.autonomy_level=result["autonomy_level"]; return result
    return router
