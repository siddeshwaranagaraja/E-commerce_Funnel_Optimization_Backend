import pandas as pd
from datetime import datetime
from src.analytics.dropoff_analysis import compute_dropoff_aggregates
from src.db.session import SessionLocal
from src.db.models import BehaviorInsight

def load_processed_data(file_path: str = "data/processed/funnel_data.csv") -> pd.DataFrame:
    """Load processed funnel data."""
    return pd.read_csv(file_path)

def calculate_dropoff_metrics(df: pd.DataFrame) -> dict:
    """Calculate dropoff analytics from processed data."""
    return compute_dropoff_aggregates(df)

def store_dropoff_analytics(metrics: dict, date_key: datetime = None) -> None:
    """Store computed dropoff metrics in the database."""
    if date_key is None:
        date_key = datetime.utcnow().date()
    
    db = SessionLocal()
    try:
        # Store detailed dropoff insights
        detailed_dropoff = metrics.get("detailed_dropoff", [])
        for dropoff_item in detailed_dropoff:
            insight = BehaviorInsight(
                insight_type="dropoff_analysis",
                description=f"Dropoff from {dropoff_item['from_stage']} to {dropoff_item['to_stage']}: "
                           f"{dropoff_item['dropoff_rate']}% ({dropoff_item['dropoff_count']} users)",
                metadata={
                    "from_stage": dropoff_item["from_stage"],
                    "to_stage": dropoff_item["to_stage"],
                    "dropoff_rate": dropoff_item["dropoff_rate"],
                    "dropoff_count": dropoff_item["dropoff_count"],
                    "date": str(date_key)
                },
                created_at=datetime.utcnow()
            )
            db.add(insight)
        
        # Store biggest leakage
        biggest = metrics.get("biggest_leakage", {})
        if biggest:
            leakage_insight = BehaviorInsight(
                insight_type="biggest_leakage",
                description=f"Biggest dropoff: {biggest['from_stage']} to {biggest['to_stage']} "
                           f"({biggest['dropoff_rate']}% - {biggest['user_loss']} users)",
                metadata={
                    "stage_transition": biggest["stage_transition"],
                    "dropoff_rate": biggest["dropoff_rate"],
                    "user_loss": biggest["user_loss"],
                    "date": str(date_key)
                },
                created_at=datetime.utcnow()
            )
            db.add(leakage_insight)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def run_dropoff_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate dropoff analysis calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_dropoff_metrics(df)
    store_dropoff_analytics(metrics)
    return metrics