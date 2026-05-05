import pandas as pd
from datetime import datetime
from src.analytics.dropoff_analysis import compute_dropoff_aggregates
from src.db.session import SessionLocal

def load_processed_data(file_path: str = "data/processed/funnel_data.csv") -> pd.DataFrame:
    """Load processed funnel data."""
    return pd.read_csv(file_path)

def calculate_dropoff_metrics(df: pd.DataFrame) -> dict:
    """Calculate dropoff analytics from processed data."""
    return compute_dropoff_aggregates(df)

def store_dropoff_analytics(metrics: dict, date_key: datetime = None) -> None:
    """Store computed dropoff metrics in the database."""
    # placeholder: persist dropoff analytics records
    pass

def run_dropoff_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate dropoff analysis calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_dropoff_metrics(df)
    store_dropoff_analytics(metrics)
    return metrics