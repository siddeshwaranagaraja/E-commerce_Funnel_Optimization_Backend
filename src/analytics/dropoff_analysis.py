import pandas as pd
from typing import Dict, List
from utils.constants import FUNNEL_STAGES
from utils.helpers import safe_divide

def calculate_stage_dropoff(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate dropoff rate for each stage."""
    dropoff_rates = {}
    
    for i in range(1, len(FUNNEL_STAGES)):
        prev_stage = FUNNEL_STAGES[i - 1]
        curr_stage = FUNNEL_STAGES[i]
        
        prev_users = df[df['funnel_stage'] == prev_stage]['user_id'].nunique()
        curr_users = df[df['funnel_stage'] == curr_stage]['user_id'].nunique()
        
        dropoff = safe_divide(prev_users - curr_users, prev_users)
        dropoff_rates[f"{prev_stage}_to_{curr_stage}"] = dropoff
    
    return dropoff_rates

def get_biggest_leakage_stage(df: pd.DataFrame) -> Dict:
    """Identify the stage with the biggest user loss."""
    dropoff_rates = calculate_stage_dropoff(df)
    
    if not dropoff_rates:
        return {}
    
    biggest_stage = max(dropoff_rates, key=dropoff_rates.get)
    return {
        "stage_transition": biggest_stage,
        "dropoff_rate": dropoff_rates[biggest_stage],
        "user_loss": df[df['funnel_stage'] == biggest_stage.split('_to_')[0]]['user_id'].nunique() - 
                      df[df['funnel_stage'] == biggest_stage.split('_to_')[1]]['user_id'].nunique()
    }

def segment_based_dropoff_comparison(df: pd.DataFrame, segment_column: str = "device_type") -> Dict[str, Dict]:
    """Compare dropoff rates across different user segments."""
    segments = df[segment_column].unique()
    segment_dropoff = {}
    
    for segment in segments:
        segment_df = df[df[segment_column] == segment]
        segment_dropoff[str(segment)] = calculate_stage_dropoff(segment_df)
    
    return segment_dropoff

def compute_dropoff_aggregates(df: pd.DataFrame) -> Dict:
    """Compute all dropoff metrics."""
    return {
        "stage_dropoff": calculate_stage_dropoff(df),
        "biggest_leakage": get_biggest_leakage_stage(df),
        "segment_comparison": segment_based_dropoff_comparison(df),
    }