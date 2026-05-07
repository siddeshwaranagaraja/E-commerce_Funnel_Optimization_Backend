import pandas as pd
from typing import Dict, List
from utils.constants import FUNNEL_STAGES
from utils.helpers import safe_divide

def calculate_stage_dropoff(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate dropoff percentage for each funnel transition."""
    dropoff_rates = {}
    
    for i in range(1, len(FUNNEL_STAGES)):
        prev_stage = FUNNEL_STAGES[i - 1]
        curr_stage = FUNNEL_STAGES[i]
        
        prev_users = df[df['funnel_stage'] == prev_stage]['user_id'].nunique()
        curr_users = df[df['funnel_stage'] == curr_stage]['user_id'].nunique()
        
        dropoff_percent = safe_divide(prev_users - curr_users, prev_users) * 100
        dropoff_rates[f"{prev_stage}_to_{curr_stage}"] = round(dropoff_percent, 2)
    
    return dropoff_rates

def calculate_detailed_dropoff(df: pd.DataFrame) -> List[Dict]:
    """Calculate detailed dropoff metrics for each transition with counts."""
    detailed = []
    
    for i in range(1, len(FUNNEL_STAGES)):
        prev_stage = FUNNEL_STAGES[i - 1]
        curr_stage = FUNNEL_STAGES[i]
        
        prev_users = df[df['funnel_stage'] == prev_stage]['user_id'].nunique()
        curr_users = df[df['funnel_stage'] == curr_stage]['user_id'].nunique()
        dropoff_users = prev_users - curr_users
        dropoff_percent = safe_divide(dropoff_users, prev_users) * 100
        
        detailed.append({
            "from_stage": prev_stage,
            "to_stage": curr_stage,
            "from_count": int(prev_users),
            "to_count": int(curr_users),
            "dropoff_count": int(dropoff_users),
            "dropoff_rate": round(dropoff_percent, 2),
        })
    
    return detailed

def get_biggest_leakage_stage(df: pd.DataFrame) -> Dict:
    """Identify the stage with the biggest user loss."""
    detailed = calculate_detailed_dropoff(df)
    
    if not detailed:
        return {}
    
    biggest = max(detailed, key=lambda x: x["dropoff_count"])
    return {
        "stage_transition": f"{biggest['from_stage']}_to_{biggest['to_stage']}",
        "from_stage": biggest["from_stage"],
        "to_stage": biggest["to_stage"],
        "dropoff_rate": biggest["dropoff_rate"],
        "user_loss": biggest["dropoff_count"],
    }

def segment_based_dropoff_comparison(df: pd.DataFrame, segment_column: str = "device_type") -> Dict[str, List[Dict]]:
    """Compare dropoff rates across different user segments."""
    if segment_column not in df.columns:
        return {}
    
    segments = df[segment_column].unique()
    segment_dropoff = {}
    
    for segment in segments:
        segment_df = df[df[segment_column] == segment]
        segment_dropoff[str(segment)] = calculate_detailed_dropoff(segment_df)
    
    return segment_dropoff

def compute_dropoff_aggregates(df: pd.DataFrame) -> Dict:
    """Compute all dropoff metrics."""
    return {
        "stage_dropoff": calculate_stage_dropoff(df),
        "detailed_dropoff": calculate_detailed_dropoff(df),
        "biggest_leakage": get_biggest_leakage_stage(df),
        "segment_comparison": segment_based_dropoff_comparison(df),
    }