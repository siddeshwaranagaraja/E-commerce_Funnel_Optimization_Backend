from fastapi import APIRouter, HTTPException
from typing import List, Dict

funnel_router = APIRouter()

@funnel_router.get("/summary")
async def get_funnel_summary():
    """Get overall funnel summary with all stages and metrics."""
    # placeholder: fetch funnel snapshot and return summary
    pass

@funnel_router.get("/conversion-summary")
async def get_conversion_summary():
    """Get conversion rate summary across all funnel stages."""
    # placeholder: calculate and return conversion rates
    pass

@funnel_router.get("/stage-trends")
async def get_stage_trend_data(stage: str = None, days: int = 30):
    """Get historical trend data for a specific funnel stage."""
    # placeholder: fetch time-series data for stage trends
    pass