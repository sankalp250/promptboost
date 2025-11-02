from pydantic import BaseModel
import datetime
import uuid
from app.models.prompt import UserAction

class PromptBase(BaseModel):
    original_prompt: str

# --- UPDATED SCHEMA ---
class PromptEnhanceRequest(PromptBase):
    # The client now sends these IDs with each request
    user_id: uuid.UUID
    session_id: uuid.UUID
    is_reroll: bool = False  # Flag to indicate if this is a reroll request
    true_original_prompt: str | None = None  # The actual original prompt for rerolls

class PromptEnhanceResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    from_cache: bool

class PromptCacheCreate(BaseModel):
    original_prompt: str
    enhanced_prompt: str

class PromptCacheDB(PromptCacheCreate):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class UsageAnalyticsCreate(BaseModel):
    prompt_id: int
    user_id: uuid.UUID
    session_id: uuid.UUID
    experiment_group: str | None = None
    enhancement_strategy: str | None = None
    user_action: UserAction | None = None

class UsageAnalyticsDB(UsageAnalyticsCreate):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class FeedbackRequest(BaseModel):
    session_id: uuid.UUID
    user_action: UserAction # Will be 'accepted' or 'rejected'

class FeedbackResponse(BaseModel):
    status: str
    message: str