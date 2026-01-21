from fastapi import APIRouter
from api.v1.endpoints import score, health, features

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    score.router,
    prefix="/score",
    tags=["Fraud Scoring"]
)

api_router.include_router(
    health.router,
    tags=["Health & Monitoring"]
)

api_router.include_router(
    features.router,
    prefix="/features",
    tags=["Feature Engineering"]
)
