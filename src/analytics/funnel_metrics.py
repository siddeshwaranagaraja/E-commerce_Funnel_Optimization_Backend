import pandas as pd
from typing import Dict, List
from datetime import datetime
from utils.constants import FUNNEL_STAGES
from utils.helpers import safe_divide

def get_stage_user_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Count unique users per funnel stage."""
    counts = {}
    for stage in FUNNEL_STAGES:
        stage_df = df[df['funnel_stage'] == stage]
        counts[stage] = stage_df['user_id'].nunique()
    return counts

def get_stage_session_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Count unique sessions per funnel stage."""
    counts = {}
    for stage in FUNNEL_STAGES:
        stage_df = df[df['funnel_stage'] == stage]
        counts[stage] = stage_df['session_id'].nunique()
    return counts

def get_step_conversion_rates(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate step-to-step conversion rates."""
    user_counts = get_stage_user_counts(df)
    rates = {}
    for i in range(1, len(FUNNEL_STAGES)):
        prev_stage = FUNNEL_STAGES[i - 1]
        curr_stage = FUNNEL_STAGES[i]
        rate = safe_divide(user_counts.get(curr_stage, 0), user_counts.get(prev_stage, 0))
        rates[f"{prev_stage}_to_{curr_stage}"] = rate
    return rates

def get_overall_conversion(df: pd.DataFrame) -> float:
    """Calculate overall conversion rate from first to last funnel stage."""
    user_counts = get_stage_user_counts(df)
    first_stage = FUNNEL_STAGES[0]
    last_stage = FUNNEL_STAGES[-1]
    return safe_divide(user_counts.get(last_stage, 0), user_counts.get(first_stage, 0))

def compute_funnel_aggregates(df: pd.DataFrame) -> Dict:
    """Compute all funnel metrics and return as a summary dict."""
    return {
        "user_counts": get_stage_user_counts(df),
        "session_counts": get_stage_session_counts(df),
        "step_conversions": get_step_conversion_rates(df),
        "overall_conversion": get_overall_conversion(df),
    }

def calculate_daily_aggregates(df: pd.DataFrame) -> List[Dict]:
    """Calculate daily funnel stage metrics for snapshot storage."""
    daily_data = []
    user_counts = get_stage_user_counts(df)
    session_counts = get_stage_session_counts(df)
    step_rates = get_step_conversion_rates(df)
    
    for i, stage in enumerate(FUNNEL_STAGES):
        dropoff_rate = 0.0
        if i > 0:
            prev_stage = FUNNEL_STAGES[i - 1]
            prev_users = user_counts.get(prev_stage, 0)
            curr_users = user_counts.get(stage, 0)
            dropoff_rate = safe_divide(prev_users - curr_users, prev_users)
        
        daily_data.append({
            "stage_name": stage,
            "users_count": user_counts.get(stage, 0),
            "sessions_count": session_counts.get(stage, 0),
            "conversion_rate": step_rates.get(f"{FUNNEL_STAGES[i-1] if i > 0 else stage}_to_{stage}", 0.0),
            "dropoff_rate": dropoff_rate,
        })
    
    return daily_data