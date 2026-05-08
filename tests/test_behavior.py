import pytest
import pandas as pd
from datetime import datetime
from src.analytics.behavior_analysis import (
    detect_repeated_browse,
    detect_cart_abandonment,
    detect_checkout_abandonment,
    extract_segment_patterns,
    compute_behavior_aggregates
)

@pytest.fixture
def sample_dataframe():
    """Sample funnel dataframe for behavior tests."""
    data = {
        'user_id': ['u1', 'u1', 'u1', 'u2', 'u2', 'u3', 'u3', 'u4', 'u5', 'u5'],
        'session_id': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10'],
        'funnel_stage': ['browse', 'browse', 'browse', 'browse', 'cart', 'cart', 'checkout', 'purchase', 'browse', 'browse'],
        'device_type': ['mobile', 'mobile', 'mobile', 'desktop', 'desktop', 'mobile', 'mobile', 'desktop', 'mobile', 'mobile'],
        'timestamp': [datetime.utcnow()] * 10,
    }
    return pd.DataFrame(data)

def test_repeated_browse_detection(sample_dataframe):
    """Test that users with 3+ browse sessions without cart are flagged."""
    result = detect_repeated_browse(sample_dataframe, threshold=3)
    
    assert isinstance(result, pd.DataFrame)
    # u1 browsed 3 times and never went to cart
    assert 'u1' in result['user_id'].values
    # u2 browsed once then went to cart, should not be flagged
    assert 'u2' not in result['user_id'].values

def test_repeated_browse_threshold(sample_dataframe):
    """Test repeated browse detection respects threshold."""
    result_high = detect_repeated_browse(sample_dataframe, threshold=5)
    result_low = detect_repeated_browse(sample_dataframe, threshold=1)
    
    assert len(result_high) <= len(result_low)

def test_cart_abandonment_detection(sample_dataframe):
    """Test cart abandonment correctly identifies users who added to cart but skipped checkout."""
    result = detect_cart_abandonment(sample_dataframe)
    
    assert isinstance(result, dict)
    assert 'cart_users' in result
    assert 'abandoned_users' in result
    assert 'abandonment_rate' in result
    assert 0 <= result['abandonment_rate'] <= 100

def test_cart_abandonment_rate_accuracy(sample_dataframe):
    """Test cart abandonment rate calculation is accurate."""
    result = detect_cart_abandonment(sample_dataframe)
    
    # u2 and u3 are in cart; u3 proceeds to checkout, u2 does not
    expected_cart_users = len(set(['u2', 'u3']))  # u2 and u3 are in cart
    assert result['cart_users'] == expected_cart_users

def test_checkout_abandonment_detection(sample_dataframe):
    """Test checkout abandonment correctly identifies users who started checkout but didn't purchase."""
    result = detect_checkout_abandonment(sample_dataframe)
    
    assert isinstance(result, dict)
    assert 'checkout_users' in result
    assert 'abandoned_users' in result
    assert 'abandonment_rate' in result
    assert 0 <= result['abandonment_rate'] <= 100

def test_checkout_abandonment_device_breakdown(sample_dataframe):
    """Test checkout abandonment includes device type breakdown."""
    result = detect_checkout_abandonment(sample_dataframe)
    
    assert 'device_breakdown' in result
    assert isinstance(result['device_breakdown'], dict)

def test_empty_dataframe():
    """Test all behavior functions handle empty dataframes gracefully."""
    empty_df = pd.DataFrame(columns=['user_id', 'session_id', 'funnel_stage', 'device_type', 'timestamp'])
    
    repeated = detect_repeated_browse(empty_df)
    assert len(repeated) == 0
    
    cart_result = detect_cart_abandonment(empty_df)
    assert cart_result['abandonment_rate'] == 0
    
    checkout_result = detect_checkout_abandonment(empty_df)
    assert checkout_result['abandonment_rate'] == 0

def test_segment_patterns_extraction(sample_dataframe):
    """Test segment pattern extraction groups correctly by segment."""
    result = extract_segment_patterns(sample_dataframe, 'device_type')
    
    assert isinstance(result, dict)
    assert 'mobile' in result or 'desktop' in result
    
    for segment_data in result.values():
        assert 'total_users' in segment_data
        assert 'cart_abandonment_rate' in segment_data
        assert 'checkout_abandonment_rate' in segment_data

def test_segment_patterns_missing_column(sample_dataframe):
    """Test segment extraction returns empty dict for missing column."""
    result = extract_segment_patterns(sample_dataframe, 'nonexistent_column')
    assert result == {}