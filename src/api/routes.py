from fastapi import APIRouter
from src.api.ingestion_routes import ingestion_router
from src.api.funnel_routes import funnel_router

api_router = APIRouter()

api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(funnel_router, prefix="/funnel", tags=["funnel"])

# Placeholder route groups:
# - /analytics - Dropoff, behavior, trends
# - /insights - AI insights and recommendations
# - /recommendations - Optimization recommendations