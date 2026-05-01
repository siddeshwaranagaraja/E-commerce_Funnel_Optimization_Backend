import pandas as pd
from src.analytics.funnel_metrics import compute_funnel_aggregates
from src.db.session import SessionLocal
from src.db.models import FunnelSnapshot

def load_processed_data(file_path: str = "data/processed/funnel_data.csv") -> pd.DataFrame:
    """Load processed funnel data."""
    # placeholder: load from CSV or DB
    return pd.read_csv(file_path)

def calculate_funnel_metrics(df: pd.DataFrame) -> dict:
    """Calculate funnel metrics from processed data."""
    return compute_funnel_aggregates(df)

def store_funnel_snapshots(metrics: dict) -> None:
    """Store computed funnel metrics as snapshots in the database."""
    # placeholder: persist FunnelSnapshot records
    pass

def run_funnel_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate funnel metrics calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_funnel_metrics(df)
    store_funnel_snapshots(metrics)
    return metrics