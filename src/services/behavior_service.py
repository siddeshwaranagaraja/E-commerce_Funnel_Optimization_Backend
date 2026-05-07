import pandas as pd
from datetime import datetime
from src.analytics.behavior_analysis import compute_behavior_aggregates
from src.db.session import SessionLocal
from src.db.models import BehaviorInsight

def load_processed_data(file_path: str = "data/processed/funnel_data.csv") -> pd.DataFrame:
    """Load processed funnel data."""
    return pd.read_csv(file_path)

def calculate_behavior_metrics(df: pd.DataFrame) -> dict:
    """Run behavior analytics on processed event data."""
    return compute_behavior_aggregates(df)

def store_behavior_insights(metrics: dict) -> None:
    """Persist behavior insights to the database."""
    # placeholder: store cart abandonment, checkout abandonment, and segment patterns
    pass

def run_behavior_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate behavior analytics calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_behavior_metrics(df)
    store_behavior_insights(metrics)
    return metrics