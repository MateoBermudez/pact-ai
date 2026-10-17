from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pact_ai.core.errors import FileRejected, LLMUnavailable


def file_rejected_handler(_: Request, exc: FileRejected) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "file_rejected", "file": exc.filename, "detail": exc.reason},
    )


def llm_unavailable_handler(_: Request, exc: LLMUnavailable) -> JSONResponse:
    return JSONResponse(status_code=502, content={"error": "ai_unavailable"})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(FileRejected, file_rejected_handler)
    app.add_exception_handler(LLMUnavailable, llm_unavailable_handler)
