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
    """Persist summarized behavior findings into the database."""
    db = SessionLocal()
    try:
        # Store cart abandonment insight
        cart_data = metrics.get("cart_abandonment", {})
        if cart_data:
            db.add(BehaviorInsight(
                insight_type="cart_abandonment",
                description=f"Cart abandonment rate: {cart_data.get('abandonment_rate', 0)}% "
                            f"({cart_data.get('abandoned_users', 0)} of {cart_data.get('cart_users', 0)} users)",
                metadata={
                    "cart_users": cart_data.get("cart_users"),
                    "abandoned_users": cart_data.get("abandoned_users"),
                    "abandonment_rate": cart_data.get("abandonment_rate"),
                    "avg_sessions_before_abandon": cart_data.get("avg_sessions_before_abandon"),
                },
                created_at=datetime.utcnow()
            ))
        
        # Store checkout abandonment insight
        checkout_data = metrics.get("checkout_abandonment", {})
        if checkout_data:
            db.add(BehaviorInsight(
                insight_type="checkout_abandonment",
                description=f"Checkout abandonment rate: {checkout_data.get('abandonment_rate', 0)}% "
                            f"({checkout_data.get('abandoned_users', 0)} of {checkout_data.get('checkout_users', 0)} users)",
                metadata={
                    "checkout_users": checkout_data.get("checkout_users"),
                    "abandoned_users": checkout_data.get("abandoned_users"),
                    "abandonment_rate": checkout_data.get("abandonment_rate"),
                    "device_breakdown": checkout_data.get("device_breakdown"),
                },
                created_at=datetime.utcnow()
            ))
        
        # Store repeated browse insight
        repeated_browse = metrics.get("repeated_browse", [])
        if repeated_browse:
            db.add(BehaviorInsight(
                insight_type="repeated_browse",
                description=f"{len(repeated_browse)} users are stuck browsing without progressing to cart.",
                metadata={"repeated_browse_users": repeated_browse},
                created_at=datetime.utcnow()
            ))
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def run_behavior_pipeline(file_path: str = "data/processed/funnel_data.csv") -> dict:
    """Orchestrate behavior analytics calculation and storage."""
    df = load_processed_data(file_path)
    metrics = calculate_behavior_metrics(df)
    store_behavior_insights(metrics)
    return metrics