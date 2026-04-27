from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from src.db.base import Base

class UserEvent(Base):
    """User event model for tracking user journey data."""
    __tablename__ = "user_events"
    # placeholder: columns for user_id, event_type, timestamp, metadata

class FunnelSnapshot(Base):
    """Funnel snapshot model for storing funnel metrics."""
    __tablename__ = "funnel_snapshots"
    # placeholder: columns for stage, count, conversion_rate, timestamp

class BehaviorInsight(Base):
    """Behavior insight model for storing user behavior patterns."""
    __tablename__ = "behavior_insights"
    # placeholder: columns for insight_type, description, metadata

class ExperimentSuggestion(Base):
    """Experiment suggestion model for A/B test ideas."""
    __tablename__ = "experiment_suggestions"
    # placeholder: columns for experiment_name, hypothesis, variants

class Recommendation(Base):
    """Recommendation model for optimization suggestions."""
    __tablename__ = "recommendations"
    # placeholder: columns for recommendation_type, description, priority