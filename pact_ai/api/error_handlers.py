from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pact_ai.core.errors import PactAiError


def pact_ai_error_handler(_: Request, error: PactAiError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(PactAiError, pact_ai_error_handler)
