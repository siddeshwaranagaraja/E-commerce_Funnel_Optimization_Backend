import pandas as pd
from datetime import datetime
from src.analytics.funnel_metrics import compute_funnel_aggregates, calculate_daily_aggregates
from src.db.session import SessionLocal
from src.db.models import FunnelSnapshot

def load_processed_data(file_path: str = "data/processed/funnel_data.csv") -> pd.DataFrame:
    """Load processed funnel data."""
    # placeholder: load from CSV or DB
    return pd.read_csv(file_path)

def calculate_funnel_metrics(df: pd.DataFrame) -> dict:
    """Calculate funnel metrics from processed data."""
    return compute_funnel_aggregates(df)

def store_funnel_snapshots(df: pd.DataFrame, date_key: datetime = None) -> None:
    """Store computed funnel metrics as daily snapshots in the database."""
    if date_key is None:
        date_key = datetime.utcnow().date()
    
    # Calculate daily aggregates
    daily_aggregates = calculate_daily_aggregates(df)
    
    # Persist each stage snapshot
    db = SessionLocal()
    try:
        for agg in daily_aggregates:
            snapshot = FunnelSnapshot(
                date_key=date_key,
                stage_name=agg["stage_name"],
                users_count=agg["users_count"],
                sessions_count=agg["sessions_count"],
                conversion_rate=agg["conversion_rate"],
                dropoff_rate=agg["dropoff_rate"],
                segment_key=None,
                created_at=datetime.utcnow()
            )
            db.add(snapshot)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def run_funnel_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate funnel metrics calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_funnel_metrics(df)
    store_funnel_snapshots(df)
    return metrics