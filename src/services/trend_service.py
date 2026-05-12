import pandas as pd
from datetime import datetime
from src.analytics.trend_analysis import compute_trend_aggregates, aggregate_snapshots_to_daily_trend
from src.db.session import SessionLocal
from src.db.models import FunnelSnapshot

def load_funnel_snapshots(days: int = 30) -> pd.DataFrame:
    """Load funnel snapshots from database for trend computation."""
    db = SessionLocal()
    try:
        snapshots = db.query(FunnelSnapshot).order_by(FunnelSnapshot.date_key.desc()).limit(days * 4).all()
        snapshot_list = [
            {
                "date_key": s.date_key,
                "stage_name": s.stage_name,
                "users_count": s.users_count,
                "sessions_count": s.sessions_count,
                "conversion_rate": s.conversion_rate,
                "dropoff_rate": s.dropoff_rate,
            }
            for s in snapshots
        ]
        return snapshot_list
    finally:
        db.close()

def compute_trends(df: pd.DataFrame = None, snapshots: list = None) -> dict:
    """Compute trend analytics from funnel data or snapshots."""
    if snapshots:
        # Use snapshots if provided
        trends = {
            "daily_conversion_trend": aggregate_snapshots_to_daily_trend(snapshots),
            "daily_dropoff_trend": [],  # Can be computed from snapshots
            "daily_segment_trend": [],
        }
    else:
        # Use dataframe
        trends = compute_trend_aggregates(df) if df is not None else {}
    
    return trends

def format_trend_response(metrics: dict) -> dict:
    """Format trend metrics for frontend consumption."""
    return {
        "status": "success",
        "data": {
            "conversion_trends": metrics.get("daily_conversion_trend", []),
            "dropoff_trends": metrics.get("daily_dropoff_trend", []),
            "segment_trends": metrics.get("daily_segment_trend", []),
        },
        "metadata": {
            "total_days": len(metrics.get("daily_conversion_trend", [])),
            "generated_at": datetime.utcnow().isoformat(),
        }
    }

def store_trend_analytics(metrics: dict) -> None:
    """Store computed trend metrics for visualization/reporting."""
    # placeholder: persist trend analytics if needed
    pass

def run_trend_pipeline(days: int = 30, use_snapshots: bool = True) -> dict:
    """Orchestrate trend analysis from snapshots or event data."""
    if use_snapshots:
        snapshots = load_funnel_snapshots(days)
        metrics = compute_trends(snapshots=snapshots)
    else:
        # For now, use processed data; later will load from snapshots
        df = pd.read_csv("data/processed/funnel_data.csv")
        metrics = compute_trends(df=df)
    
    store_trend_analytics(metrics)
    return format_trend_response(metrics)