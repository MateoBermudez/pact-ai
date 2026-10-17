from fastapi import APIRouter

from pact_ai.api.routes import health, review, screening, structure

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(structure.router)
api_router.include_router(review.router)
api_router.include_router(screening.router)
