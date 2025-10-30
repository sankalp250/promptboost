import datetime
import uuid
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# New Enum for user actions
class UserAction(str, enum.Enum):
    accepted = "accepted"
    rejected = "rejected"
    modified = "modified"


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
    Tracks metrics related to prompt enhancements and A/B tests.
    """
    __tablename__ = "usage_analytics"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompt_cache.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # --- NEW COLUMNS FOR A/B TESTING ---
    user_id = Column(UUID(as_uuid=True), default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    experiment_group = Column(String(50), nullable=True)  # e.g., 'A', 'B'
    enhancement_strategy = Column(String(100), nullable=True)  # e.g., 'basic_v1'
    user_action = Column(SQLAlchemyEnum(UserAction), nullable=True)  # 'accepted', 'rejected'

    # Relationship to prompt_cache
    prompt = relationship("PromptCache", back_populates="analytics")