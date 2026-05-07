import pandas as pd
from typing import Dict, List
from utils.constants import FUNNEL_STAGES
from utils.helpers import safe_divide

def detect_repeated_browse(df: pd.DataFrame, threshold: int = 3) -> pd.DataFrame:
    """Detect users who visited the browse stage multiple times without progressing."""
    browse_df = df[df['funnel_stage'] == 'browse']
    browse_counts = browse_df.groupby('user_id')['session_id'].nunique().reset_index()
    browse_counts.columns = ['user_id', 'browse_session_count']
    
    repeated = browse_counts[browse_counts['browse_session_count'] >= threshold]
    return repeated

def detect_cart_abandonment(df: pd.DataFrame) -> Dict:
    """Detect users who added to cart but did not proceed to checkout."""
    cart_users = set(df[df['funnel_stage'] == 'cart']['user_id'].unique())
    checkout_users = set(df[df['funnel_stage'] == 'checkout']['user_id'].unique())
    
    abandoned_users = cart_users - checkout_users
    abandonment_rate = safe_divide(len(abandoned_users), len(cart_users)) * 100
    
    return {
        "cart_users": len(cart_users),
        "abandoned_users": len(abandoned_users),
        "abandonment_rate": round(abandonment_rate, 2),
        "user_ids": list(abandoned_users)
    }

def detect_checkout_abandonment(df: pd.DataFrame) -> Dict:
    """Detect users who started checkout but did not complete purchase."""
    checkout_users = set(df[df['funnel_stage'] == 'checkout']['user_id'].unique())
    purchase_users = set(df[df['funnel_stage'] == 'purchase']['user_id'].unique())
    
    abandoned_users = checkout_users - purchase_users
    abandonment_rate = safe_divide(len(abandoned_users), len(checkout_users)) * 100
    
    return {
        "checkout_users": len(checkout_users),
        "abandoned_users": len(abandoned_users),
        "abandonment_rate": round(abandonment_rate, 2),
        "user_ids": list(abandoned_users)
    }

def extract_segment_patterns(df: pd.DataFrame, segment_column: str = "device_type") -> Dict[str, Dict]:
    """Extract behavior patterns across different user segments."""
    if segment_column not in df.columns:
        return {}
    
    segments = df[segment_column].unique()
    segment_patterns = {}
    
    for segment in segments:
        segment_df = df[df[segment_column] == segment]
        cart_aband = detect_cart_abandonment(segment_df)
        checkout_aband = detect_checkout_abandonment(segment_df)
        
        segment_patterns[str(segment)] = {
            "total_users": segment_df['user_id'].nunique(),
            "cart_abandonment_rate": cart_aband["abandonment_rate"],
            "checkout_abandonment_rate": checkout_aband["abandonment_rate"],
            "stage_distribution": {
                stage: segment_df[segment_df['funnel_stage'] == stage]['user_id'].nunique()
                for stage in FUNNEL_STAGES
            }
        }
    
    return segment_patterns

def compute_behavior_aggregates(df: pd.DataFrame) -> Dict:
    """Compute all behavior metrics."""
    return {
        "repeated_browse": detect_repeated_browse(df).to_dict(orient='records'),
        "cart_abandonment": detect_cart_abandonment(df),
        "checkout_abandonment": detect_checkout_abandonment(df),
        "segment_patterns": extract_segment_patterns(df),
    }