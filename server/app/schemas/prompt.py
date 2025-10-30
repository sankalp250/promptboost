from pydantic import BaseModel
import datetime
import uuid
from app.models.prompt import UserAction # Import the Enum

class PromptBase(BaseModel):
    original_prompt: str

class PromptEnhanceRequest(PromptBase):
    pass # No changes needed here yet

class PromptEnhanceResponse(BaseModel):
    # This remains the same, it's what we return to the client
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

# --- NEW SCHEMA FOR CREATING ANALYTICS ENTRIES ---
class UsageAnalyticsCreate(BaseModel):
    prompt_id: int
    user_id: uuid.UUID
    session_id: uuid.UUID
    experiment_group: str | None = None
    enhancement_strategy: str | None = None
    user_action: UserAction | None = None # Use the imported Enum

# --- NEW SCHEMA FOR DATABASE-READ ANALYTICS ---
class UsageAnalyticsDB(UsageAnalyticsCreate):
    id: int
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True