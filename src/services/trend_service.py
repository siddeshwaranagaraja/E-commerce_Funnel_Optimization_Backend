import pandas as pd
from datetime import datetime
from src.analytics.trend_analysis import compute_trend_aggregates
from src.db.session import SessionLocal

def load_funnel_snapshots(days: int = 30) -> pd.DataFrame:
    """Load funnel snapshots from database for trend computation."""
    # placeholder: query FunnelSnapshot table for last N days
    pass

def compute_trends(df: pd.DataFrame) -> dict:
    """Compute trend analytics from funnel data or snapshots."""
    return compute_trend_aggregates(df)

def store_trend_analytics(metrics: dict) -> None:
    """Store computed trend metrics for visualization/reporting."""
    # placeholder: persist trend analytics if needed
    pass

def run_trend_pipeline(days: int = 30) -> dict:
    """Orchestrate trend analysis from snapshots and event data."""
    # For now, use processed data; later will load from snapshots
    df = pd.read_csv("data/processed/funnel_data.csv")
    metrics = compute_trends(df)
    store_trend_analytics(metrics)
    return metrics

import pandas as pd