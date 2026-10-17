from fastapi import FastAPI

from pact_ai.api.error_handlers import register_error_handlers
from pact_ai.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="PACT AI", version="0.3.0")
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
