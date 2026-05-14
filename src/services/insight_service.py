from typing import Dict, List
from src.insights.rules_engine import RulesEngine
from src.services.funnel_service import run_funnel_pipeline
from src.services.dropoff_service import run_dropoff_pipeline
from src.services.behavior_service import run_behavior_pipeline
from src.services.trend_service import run_trend_pipeline
from src.db.session import SessionLocal
from src.db.models import BehaviorInsight
from datetime import datetime

def combine_analytics_inputs(funnel_metrics: Dict, dropoff_metrics: Dict, behavior_metrics: Dict, trend_metrics: Dict = None) -> Dict:
    """Combine outputs from all analytics services into a single input for the rules engine."""
    return {
        "funnel_data": funnel_metrics,
        "dropoff_data": dropoff_metrics,
        "behavior_data": behavior_metrics,
        "trends_data": trend_metrics or {},
    }

def generate_insights(analytics_inputs: Dict) -> List[Dict]:
    """Run rules engine on combined analytics inputs to generate insights."""
    insights = RulesEngine.run_all_rules(
        funnel_data=analytics_inputs.get("funnel_data", {}),
        dropoff_data=analytics_inputs.get("dropoff_data", {}),
        behavior_data=analytics_inputs.get("behavior_data", {}),
        trends_data=analytics_inputs.get("trends_data", {}),
    )
    return insights

def assemble_insight_response(insights: List[Dict]) -> Dict:
    """Assemble final structured response with insight summary and detail."""
    triggered = [i for i in insights if i.get("triggered")]
    
    severity_counts = {"critical": 0, "high": 0, "medium": 0}
    for insight in triggered:
        sev = insight.get("severity", "medium")
        if sev in severity_counts:
            severity_counts[sev] += 1
    
    return {
        "summary": {
            "total_insights": len(triggered),
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "generated_at": datetime.utcnow().isoformat(),
        },
        "insights": triggered,
    }

def store_insights(insights: List[Dict]) -> None:
    """Persist generated insights to BehaviorInsight table."""
    db = SessionLocal()
    try:
        for insight in insights:
            if insight.get("triggered"):
                db.add(BehaviorInsight(
                    insight_type=insight.get("rule_name"),
                    description=insight.get("description"),
                    metadata={
                        "severity": insight.get("severity"),
                        "value": insight.get("value"),
                        "recommendation": insight.get("recommendation"),
                        "context": insight.get("context", {}),
                        "generated_at": insight.get("generated_at"),
                    },
                    created_at=datetime.utcnow()
                ))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def run_insight_pipeline(file_path: str = "data/processed/funnel_data.csv") -> Dict:
    """Orchestrate full insight generation pipeline from raw analytics."""
    # Run all analytics pipelines
    funnel_metrics = run_funnel_pipeline(file_path)
    dropoff_metrics = run_dropoff_pipeline(file_path)
    behavior_metrics = run_behavior_pipeline(file_path)
    trend_metrics = run_trend_pipeline()
    
    # Combine inputs
    analytics_inputs = combine_analytics_inputs(
        funnel_metrics,
        dropoff_metrics,
        behavior_metrics,
        trend_metrics
    )
    
    # Generate insights
    insights = generate_insights(analytics_inputs)
    
    # Store insights
    store_insights(insights)
    
    # Assemble and return structured response
    return assemble_insight_response(insights)