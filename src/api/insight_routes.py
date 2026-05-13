from fastapi import APIRouter, HTTPException
from typing import Optional

insight_router = APIRouter()

@insight_router.get("/summary")
async def get_insight_summary():
    """Get summary of all triggered insights with counts and priorities."""
    # placeholder: return high-level insight summary
    pass

@insight_router.get("/detail")
async def get_insight_detail(insight_id: Optional[str] = None):
    """Get detailed information about specific insights with recommendations."""
    # placeholder: return detailed insights with full context and actionable recommendations
    pass