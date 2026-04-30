from fastapi import APIRouter
from src.api.ingestion_routes import ingestion_router

api_router = APIRouter()

api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])

# Placeholder route groups:
# - /analytics - Funnel, dropoff, behavior, trends
# - /insights - AI insights and recommendations
# - /recommendations - Optimization recommendations