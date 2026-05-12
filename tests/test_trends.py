import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.analytics.trend_analysis import (
    calculate_daily_conversion_trend,
    calculate_daily_dropoff_trend,
    calculate_daily_segment_trend,
    aggregate_snapshots_to_daily_trend,
)
from src.services.trend_service import format_trend_response

@pytest.fixture
def sample_dataframe():
    """Create sample dataframe spanning multiple days."""
    today = datetime.utcnow()
    data_list = []
    
    for day_offset in range(5):
        date = today - timedelta(days=day_offset)
        for i in range(10):
            data_list.append({
                'user_id': f'u{i}',
                'session_id': f's{i}_{day_offset}',
                'funnel_stage': ['browse', 'cart', 'checkout', 'purchase'][i % 4],
                'device_type': 'mobile' if i % 2 == 0 else 'desktop',
                'timestamp': date,
            })
    
    return pd.DataFrame(data_list)

@pytest.fixture
def sample_snapshots():
    """Create sample funnel snapshot records."""
    snapshots = []
    today = datetime.utcnow()
    
    for day_offset in range(5):
        date = today - timedelta(days=day_offset)
        for stage_idx, stage in enumerate(['browse', 'cart', 'checkout', 'purchase']):
            snapshots.append({
                "date_key": date,
                "stage_name": stage,
                "users_count": 100 - (stage_idx * 25),
                "sessions_count": 120 - (stage_idx * 30),
                "conversion_rate": 0.8 - (stage_idx * 0.1),
                "dropoff_rate": 0.2 + (stage_idx * 0.1),
            })
    
    return snapshots

def test_daily_conversion_trend_output(sample_dataframe):
    """Test daily conversion trend returns correct structure."""
    trend = calculate_daily_conversion_trend(sample_dataframe)
    
    assert isinstance(trend, list)
    assert len(trend) > 0
    
    # Check structure of each daily entry
    for day in trend:
        assert 'date' in day
        assert 'conversion_rate' in day
        assert 'browse_users' in day
        assert 'purchase_users' in day
        assert 0 <= day['conversion_rate'] <= 100

def test_daily_conversion_rate_accuracy(sample_dataframe):
    """Test conversion rate calculation accuracy."""
    trend = calculate_daily_conversion_trend(sample_dataframe)
    
    for day in trend:
        browse_users = day.get('browse_users', 0)
        purchase_users = day.get('purchase_users', 0)
        expected_rate = (purchase_users / browse_users * 100) if browse_users > 0 else 0
        assert abs(day['conversion_rate'] - round(expected_rate, 2)) < 0.01

def test_daily_dropoff_trend_output(sample_dataframe):
    """Test daily dropoff trend returns correct structure."""
    trend = calculate_daily_dropoff_trend(sample_dataframe)
    
    assert isinstance(trend, list)
    assert len(trend) > 0
    
    for day in trend:
        assert 'date' in day
        assert 'browse_to_cart_dropoff' in day
        assert 'cart_to_checkout_dropoff' in day
        assert 'checkout_to_purchase_dropoff' in day
        assert 0 <= day['browse_to_cart_dropoff'] <= 100

def test_empty_dataframe_handling():
    """Test trend functions handle empty dataframes gracefully."""
    empty_df = pd.DataFrame({
        'user_id': [],
        'session_id': [],
        'funnel_stage': [],
        'timestamp': []
    })
    
    conversion_trend = calculate_daily_conversion_trend(empty_df)
    assert conversion_trend == []
    
    dropoff_trend = calculate_daily_dropoff_trend(empty_df)
    assert dropoff_trend == []
    
    segment_trend = calculate_daily_segment_trend(empty_df)
    assert segment_trend == []

def test_missing_timestamp_column():
    """Test trend functions handle missing timestamp column."""
    df_no_timestamp = pd.DataFrame({
        'user_id': ['u1', 'u2'],
        'funnel_stage': ['browse', 'cart']
    })
    
    trend = calculate_daily_conversion_trend(df_no_timestamp)
    assert trend == []

def test_aggregate_snapshots_to_trend(sample_snapshots):
    """Test aggregating snapshots into daily trends."""
    trend = aggregate_snapshots_to_daily_trend(sample_snapshots)
    
    assert isinstance(trend, list)
    assert len(trend) > 0
    
    for day in trend:
        assert 'date' in day
        assert 'browse_users' in day
        assert 'purchase_users' in day
        assert 'overall_conversion_rate' in day

def test_empty_snapshots_list():
    """Test aggregating empty snapshots list."""
    trend = aggregate_snapshots_to_daily_trend([])
    assert trend == []

def test_format_trend_response():
    """Test trend response formatting for frontend."""
    metrics = {
        "daily_conversion_trend": [{"date": "2026-05-12", "conversion_rate": 25.5}],
        "daily_dropoff_trend": [{"date": "2026-05-12", "browse_to_cart_dropoff": 20.0}],
        "daily_segment_trend": [{"date": "2026-05-12", "segments": {}}],
    }
    
    response = format_trend_response(metrics)
    
    assert response["status"] == "success"
    assert "data" in response
    assert "metadata" in response
    assert response["data"]["conversion_trends"] == metrics["daily_conversion_trend"]
    assert response["metadata"]["total_days"] == 1