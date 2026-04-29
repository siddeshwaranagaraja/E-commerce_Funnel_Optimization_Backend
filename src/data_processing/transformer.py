import pandas as pd
from utils.constants import FUNNEL_STAGES

EVENT_TO_STAGE = {
    'view': 'browse',
    'browse': 'browse',
    'product_view': 'browse',
    'add_to_cart': 'cart',
    'cart': 'cart',
    'remove_from_cart': 'cart',
    'begin_checkout': 'checkout',
    'checkout': 'checkout',
    'payment': 'checkout',
    'purchase': 'purchase',
    'order': 'purchase',
    'complete_purchase': 'purchase'
}

def map_funnel_stages(df: pd.DataFrame) -> pd.DataFrame:
    """Map events to funnel stages (browse, cart, checkout, purchase)."""
    df['funnel_stage'] = df['event_type'].map(EVENT_TO_STAGE)
    return df

def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize timestamp columns to consistent format."""
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def group_by_session(df: pd.DataFrame) -> pd.DataFrame:
    """Group events by user session."""
    return df.sort_values(['session_id', 'timestamp'])

def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all transformation steps."""
    df = normalize_timestamps(df)
    df = map_funnel_stages(df)
    df = group_by_session(df)
    return df