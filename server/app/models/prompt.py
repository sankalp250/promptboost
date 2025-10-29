import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class PromptCache(Base):
    """
    SQLAlchemy model for the prompt_cache table.
    Stores original and enhanced prompts to avoid re-calling the LLM API.
    """
    __tablename__ = "prompt_cache"

    id = Column(Integer, primary_key=True, index=True)
    original_prompt = Column(Text, nullable=False, unique=True, index=True)
    enhanced_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to usage_analytics
    analytics = relationship("UsageAnalytics", back_populates="prompt")

class UsageAnalytics(Base):
    """
    SQLAlchemy model for the usage_analytics table.
    Tracks metrics related to prompt enhancements.
    """
    __tablename__ = "usage_analytics"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompt_cache.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Add more fields later like enhancement_time_ms, user_feedback, etc.

    # Relationship to prompt_cache
    prompt = relationship("PromptCache", back_populates="analytics")