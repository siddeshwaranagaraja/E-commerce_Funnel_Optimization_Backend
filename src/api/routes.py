from fastapi import APIRouter
from src.api.ingestion_routes import ingestion_router
from src.api.funnel_routes import funnel_router
from src.api.dropoff_routes import dropoff_router
from src.api.behavior_routes import behavior_router

api_router = APIRouter()

api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(funnel_router, prefix="/funnel", tags=["funnel"])
api_router.include_router(dropoff_router, prefix="/dropoff", tags=["dropoff"])
api_router.include_router(behavior_router, prefix="/behavior", tags=["behavior"])

# Placeholder route groups:
# - /trends - Trend analysis
# - /insights - AI insights and recommendations
# - /recommendations - Optimization recommendations