import pytest
import pandas as pd
from datetime import datetime
from src.analytics.dropoff_analysis import (
    calculate_stage_dropoff,
    calculate_detailed_dropoff,
    get_biggest_leakage_stage,
    segment_based_dropoff_comparison,
    compute_dropoff_aggregates
)

@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    data = {
        'user_id': ['u1', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', 'u10'] * 10,
        'session_id': [f's{i}' for i in range(100)],
        'funnel_stage': ['browse'] * 50 + ['cart'] * 35 + ['checkout'] * 20 + ['purchase'] * 15,
        'device_type': ['mobile'] * 50 + ['desktop'] * 50,
        'timestamp': [datetime.utcnow()] * 100,
    }
    return pd.DataFrame(data)

def test_stage_dropoff_percentages(sample_dataframe):
    """Test dropoff percentage calculation for each stage."""
    dropoff_rates = calculate_stage_dropoff(sample_dataframe)
    
    assert isinstance(dropoff_rates, dict)
    assert 'browse_to_cart' in dropoff_rates
    assert 'cart_to_checkout' in dropoff_rates
    assert 'checkout_to_purchase' in dropoff_rates
    
    # Check that dropoff rates are percentages
    for rate in dropoff_rates.values():
        assert 0 <= rate <= 100

def test_detailed_dropoff_counts(sample_dataframe):
    """Test detailed dropoff calculation with user counts."""
    detailed = calculate_detailed_dropoff(sample_dataframe)
    
    assert isinstance(detailed, list)
    assert len(detailed) > 0
    
    for item in detailed:
        assert 'from_stage' in item
        assert 'to_stage' in item
        assert 'dropoff_count' in item
        assert 'dropoff_rate' in item
        assert item['from_count'] >= item['to_count']

def test_biggest_leakage_stage(sample_dataframe):
    """Test identification of biggest user loss stage."""
    biggest = get_biggest_leakage_stage(sample_dataframe)
    
    assert isinstance(biggest, dict)
    assert 'stage_transition' in biggest
    assert 'dropoff_rate' in biggest
    assert 'user_loss' in biggest

def test_segment_dropoff_comparison(sample_dataframe):
    """Test segment-based dropoff comparison."""
    comparison = segment_based_dropoff_comparison(sample_dataframe, 'device_type')
    
    assert isinstance(comparison, dict)
    assert 'mobile' in comparison or 'desktop' in comparison

def test_invalid_dataset():
    """Test handling of invalid or empty dataset."""
    empty_df = pd.DataFrame({'user_id': [], 'funnel_stage': []})
    
    dropoff = calculate_stage_dropoff(empty_df)
    assert isinstance(dropoff, dict)

def test_missing_funnel_stage_column():
    """Test handling of missing funnel_stage column."""
    invalid_df = pd.DataFrame({'user_id': ['u1', 'u2'], 'session_id': ['s1', 's2']})
    
    with pytest.raises(KeyError):
        calculate_detailed_dropoff(invalid_df)