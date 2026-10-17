from fastapi import APIRouter

from pact_ai.api.routes import agreements, health, reviews

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(agreements.router)
api_router.include_router(reviews.router)
