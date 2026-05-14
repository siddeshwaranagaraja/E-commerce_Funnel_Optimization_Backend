import pytest
from src.insights.rules_engine import RulesEngine, build_insight_payload
from src.services.insight_service import generate_insights, assemble_insight_response, combine_analytics_inputs

# ---------- Fixtures ----------

@pytest.fixture
def dropoff_data_high():
    return {
        "detailed_dropoff": [
            {"from_stage": "browse", "to_stage": "cart", "dropoff_rate": 65.0, "dropoff_count": 350},
            {"from_stage": "cart", "to_stage": "checkout", "dropoff_rate": 25.0, "dropoff_count": 88},
        ]
    }

@pytest.fixture
def dropoff_data_low():
    return {
        "detailed_dropoff": [
            {"from_stage": "browse", "to_stage": "cart", "dropoff_rate": 20.0, "dropoff_count": 50},
        ]
    }

@pytest.fixture
def behavior_data_high():
    return {
        "cart_abandonment": {"cart_users": 200, "abandoned_users": 120, "abandonment_rate": 60.0, "avg_sessions_before_abandon": 2.3},
        "checkout_abandonment": {"checkout_users": 80, "abandoned_users": 45, "abandonment_rate": 56.25, "device_breakdown": {"mobile": 30, "desktop": 15}},
        "repeated_browse": [{"user_id": f"u{i}", "browse_session_count": 4} for i in range(10)],
        "segment_patterns": {},
    }

@pytest.fixture
def behavior_data_low():
    return {
        "cart_abandonment": {"cart_users": 200, "abandoned_users": 30, "abandonment_rate": 15.0, "avg_sessions_before_abandon": 1.1},
        "checkout_abandonment": {"checkout_users": 170, "abandoned_users": 20, "abandonment_rate": 11.8, "device_breakdown": {}},
        "repeated_browse": [],
        "segment_patterns": {},
    }

# ---------- build_insight_payload ----------

def test_build_insight_payload_structure():
    payload = build_insight_payload("test_rule", "high", "Test description", 75.0, "Fix it.")
    assert payload["triggered"] is True
    assert payload["rule_name"] == "test_rule"
    assert payload["severity"] == "high"
    assert payload["value"] == 75.0
    assert "generated_at" in payload
    assert "context" in payload

# ---------- check_high_browse_to_cart_dropoff ----------

def test_high_browse_cart_dropoff_triggered(dropoff_data_high):
    result = RulesEngine.check_high_browse_to_cart_dropoff(dropoff_data_high["detailed_dropoff"])
    assert result["triggered"] is True
    assert result["rule_name"] == "high_browse_cart_dropoff"
    assert result["severity"] in ("high", "medium")
    assert result["value"] == 65.0

def test_high_browse_cart_dropoff_not_triggered(dropoff_data_low):
    result = RulesEngine.check_high_browse_to_cart_dropoff(dropoff_data_low["detailed_dropoff"])
    assert result["triggered"] is False

# ---------- check_high_cart_abandonment ----------

def test_high_cart_abandonment_triggered(behavior_data_high):
    result = RulesEngine.check_high_cart_abandonment(behavior_data_high)
    assert result["triggered"] is True
    assert result["rule_name"] == "high_cart_abandonment"
    assert result["severity"] == "high"
    assert result["context"]["cart_users"] == 200

def test_high_cart_abandonment_not_triggered(behavior_data_low):
    result = RulesEngine.check_high_cart_abandonment(behavior_data_low)
    assert result["triggered"] is False

# ---------- check_high_checkout_abandonment ----------

def test_high_checkout_abandonment_triggered_critical(behavior_data_high):
    result = RulesEngine.check_high_checkout_abandonment(behavior_data_high)
    assert result["triggered"] is True
    assert result["rule_name"] == "high_checkout_abandonment"
    assert result["severity"] == "critical"
    assert "device_breakdown" in result["context"]

def test_high_checkout_abandonment_not_triggered(behavior_data_low):
    result = RulesEngine.check_high_checkout_abandonment(behavior_data_low)
    assert result["triggered"] is False

# ---------- check_weak_returning_user_conversion ----------

def test_weak_returning_user_conversion_triggered(behavior_data_high):
    result = RulesEngine.check_weak_returning_user_conversion(behavior_data_high, {})
    assert result["triggered"] is True
    assert result["rule_name"] == "weak_returning_user_conversion"
    assert result["context"]["returning_user_count"] == 10

def test_weak_returning_user_no_users(behavior_data_low):
    result = RulesEngine.check_weak_returning_user_conversion(behavior_data_low, {})
    assert result["triggered"] is False

# ---------- run_all_rules ----------

def test_run_all_rules_returns_sorted_by_severity(dropoff_data_high, behavior_data_high):
    insights = RulesEngine.run_all_rules(
        funnel_data={},
        dropoff_data=dropoff_data_high,
        behavior_data=behavior_data_high,
    )
    
    assert isinstance(insights, list)
    assert len(insights) > 0
    
    # Verify sorted order: critical before high before medium
    severity_order = {"critical": 0, "high": 1, "medium": 2}
    for i in range(len(insights) - 1):
        assert severity_order.get(insights[i]["severity"], 3) <= severity_order.get(insights[i + 1]["severity"], 3)

def test_run_all_rules_no_insights_low_data(dropoff_data_low, behavior_data_low):
    insights = RulesEngine.run_all_rules(
        funnel_data={},
        dropoff_data=dropoff_data_low,
        behavior_data=behavior_data_low,
    )
    assert insights == []

# ---------- assemble_insight_response ----------

def test_assemble_insight_response(dropoff_data_high, behavior_data_high):
    insights = RulesEngine.run_all_rules({}, dropoff_data_high, behavior_data_high)
    response = assemble_insight_response(insights)
    
    assert "summary" in response
    assert "insights" in response
    assert response["summary"]["total_insights"] == len(insights)
    assert response["summary"]["critical_count"] >= 0
    assert "generated_at" in response["summary"]
