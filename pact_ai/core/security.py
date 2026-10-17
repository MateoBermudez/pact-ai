import hmac
from typing import Annotated

from fastapi import Header, HTTPException

from pact_ai.core.config import get_settings


def require_secret(x_pact_ai_secret: Annotated[str | None, Header()] = None) -> None:
    expected = get_settings().shared_secret
    if not expected:
        return
    if not x_pact_ai_secret or not hmac.compare_digest(x_pact_ai_secret, expected):
        raise HTTPException(status_code=401, detail="No autorizado")
