import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from utils.constants import FUNNEL_STAGES
from utils.helpers import safe_divide

def aggregate_snapshots_to_daily_trend(snapshots: List[Dict]) -> List[Dict]:
    """Aggregate FunnelSnapshot records into daily trend data."""
    if not snapshots:
        return []
    
    # Group snapshots by date
    snapshot_df = pd.DataFrame(snapshots)
    if snapshot_df.empty:
        return []
    
    snapshot_df['date'] = pd.to_datetime(snapshot_df['date_key']).dt.date
    daily_trend = []
    
    for date in sorted(snapshot_df['date'].unique()):
        daily_snapshots = snapshot_df[snapshot_df['date'] == date]
        daily_data = {"date": str(date)}
        
        # Aggregate metrics by stage
        for stage in FUNNEL_STAGES:
            stage_data = daily_snapshots[daily_snapshots['stage_name'] == stage]
            if not stage_data.empty:
                daily_data[f"{stage}_users"] = int(stage_data['users_count'].sum())
                daily_data[f"{stage}_sessions"] = int(stage_data['sessions_count'].sum())
                daily_data[f"{stage}_conversion_rate"] = round(stage_data['conversion_rate'].mean(), 2)
        
        # Calculate overall conversion
        browse_users = daily_data.get('browse_users', 0)
        purchase_users = daily_data.get('purchase_users', 0)
        overall_conversion = safe_divide(purchase_users, browse_users) * 100 if browse_users > 0 else 0
        daily_data["overall_conversion_rate"] = round(overall_conversion, 2)
        
        daily_trend.append(daily_data)
    
    return daily_trend

def calculate_daily_conversion_trend(df: pd.DataFrame, days: int = 30) -> List[Dict]:
    """Calculate daily conversion rates across funnel stages."""
    if 'timestamp' not in df.columns:
        return []
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_trend = []
    
    for date in sorted(df['date'].unique()):
        daily_df = df[df['date'] == date]
        
        # Calculate stage-wise user counts
        daily_data = {"date": str(date)}
        
        for stage in FUNNEL_STAGES:
            stage_users = daily_df[daily_df['funnel_stage'] == stage]['user_id'].nunique()
            daily_data[f"{stage}_users"] = int(stage_users)
        
        # Calculate overall conversion
        browse_users = daily_data.get('browse_users', 0)
        purchase_users = daily_data.get('purchase_users', 0)
        conversion_rate = safe_divide(purchase_users, browse_users) * 100 if browse_users > 0 else 0
        daily_data["conversion_rate"] = round(conversion_rate, 2)
        
        daily_trend.append(daily_data)
    
    return daily_trend

def calculate_daily_dropoff_trend(df: pd.DataFrame, days: int = 30) -> List[Dict]:
    """Calculate daily dropoff rates for each funnel transition."""
    if 'timestamp' not in df.columns:
        return []
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_trend = []
    
    for date in sorted(df['date'].unique()):
        daily_df = df[df['date'] == date]
        daily_data = {"date": str(date)}
        
        # Calculate dropoff for each transition
        for i in range(1, len(FUNNEL_STAGES)):
            prev_stage = FUNNEL_STAGES[i - 1]
            curr_stage = FUNNEL_STAGES[i]
            
            prev_users = daily_df[daily_df['funnel_stage'] == prev_stage]['user_id'].nunique()
            curr_users = daily_df[daily_df['funnel_stage'] == curr_stage]['user_id'].nunique()
            
            dropoff_rate = safe_divide(prev_users - curr_users, prev_users) * 100 if prev_users > 0 else 0
            daily_data[f"{prev_stage}_to_{curr_stage}_dropoff"] = round(dropoff_rate, 2)
        
        daily_trend.append(daily_data)
    
    return daily_trend

def calculate_daily_segment_trend(df: pd.DataFrame, segment_column: str = "device_type", days: int = 30) -> List[Dict]:
    """Calculate daily conversion trends for each user segment."""
    if segment_column not in df.columns or 'timestamp' not in df.columns:
        return []
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    segment_trend = []
    
    segments = df[segment_column].dropna().unique()
    
    for date in sorted(df['date'].unique()):
        daily_df = df[df['date'] == date]
        date_data = {"date": str(date), "segments": {}}
        
        for segment in segments:
            segment_df = daily_df[daily_df[segment_column] == segment]
            
            # Calculate conversion for segment
            browse_users = segment_df[segment_df['funnel_stage'] == 'browse']['user_id'].nunique()
            purchase_users = segment_df[segment_df['funnel_stage'] == 'purchase']['user_id'].nunique()
            conversion_rate = safe_divide(purchase_users, browse_users) * 100 if browse_users > 0 else 0
            
            date_data["segments"][str(segment)] = {
                "users": segment_df['user_id'].nunique(),
                "browse_users": int(browse_users),
                "purchase_users": int(purchase_users),
                "conversion_rate": round(conversion_rate, 2),
            }
        
        segment_trend.append(date_data)
    
    return segment_trend

def compute_trend_aggregates(df: pd.DataFrame) -> Dict:
    """Compute all trend metrics."""
    return {
        "daily_conversion_trend": calculate_daily_conversion_trend(df),
        "daily_dropoff_trend": calculate_daily_dropoff_trend(df),
        "daily_segment_trend": calculate_daily_segment_trend(df),
    }
    }