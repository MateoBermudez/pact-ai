import hmac
from typing import Annotated

from fastapi import Depends, Header, HTTPException

from pact_ai.core.config import Settings, get_settings


def require_internal_token(
    settings: Annotated[Settings, Depends(get_settings)],
    x_internal_token: Annotated[str | None, Header()] = None,
) -> None:
    if not settings.internal_token:
        return
    if x_internal_token is None or not hmac.compare_digest(x_internal_token, settings.internal_token):
        raise HTTPException(status_code=401, detail="unauthorized")
