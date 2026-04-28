from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text
from src.db.base import Base

class UserEvent(Base):
    """User event model for tracking user journey data."""
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    product_id = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    source_channel = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=DateTime.utcnow)

class FunnelSnapshot(Base):
    """Funnel snapshot model for storing funnel metrics."""
    __tablename__ = "funnel_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date_key = Column(DateTime, nullable=False, index=True)
    stage_name = Column(String, nullable=False)
    users_count = Column(Integer, nullable=False)
    sessions_count = Column(Integer, nullable=False)
    conversion_rate = Column(Float, nullable=True)
    dropoff_rate = Column(Float, nullable=True)
    segment_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=DateTime.utcnow)

class BehaviorInsight(Base):
    """Behavior insight model for storing user behavior patterns."""
    __tablename__ = "behavior_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=DateTime.utcnow)

class ExperimentSuggestion(Base):
    """Experiment suggestion model for A/B test ideas."""
    __tablename__ = "experiment_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String, nullable=False)
    hypothesis = Column(Text, nullable=False)
    variants = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=DateTime.utcnow)

class Recommendation(Base):
    """Recommendation model for optimization suggestions."""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=DateTime.utcnow)