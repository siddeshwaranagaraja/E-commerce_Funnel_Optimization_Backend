from fastapi import APIRouter
from src.api.ingestion_routes import ingestion_router
from src.api.funnel_routes import funnel_router
from src.api.dropoff_routes import dropoff_router
from src.api.behavior_routes import behavior_router
from src.api.trend_routes import trend_router
from src.api.insight_routes import insight_router

api_router = APIRouter()

api_router.include_router(ingestion_router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(funnel_router, prefix="/funnel", tags=["funnel"])
api_router.include_router(dropoff_router, prefix="/dropoff", tags=["dropoff"])
api_router.include_router(behavior_router, prefix="/behavior", tags=["behavior"])
api_router.include_router(trend_router, prefix="/trends", tags=["trends"])
api_router.include_router(insight_router, prefix="/insights", tags=["insights"])

# Placeholder route groups:
# - /recommendations - Optimization recommendations