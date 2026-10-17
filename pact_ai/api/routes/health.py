from fastapi import APIRouter

from pact_ai.core.dependencies import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: SettingsDep) -> dict[str, str | bool]:
    return {
        "status": "ok",
        "model": settings.gemini_model,
        "gemini_configured": bool(settings.gemini_api_key),
    }
