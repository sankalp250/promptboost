from pydantic import BaseModel
import datetime

class PromptBase(BaseModel):
    original_prompt: str

class PromptEnhanceRequest(PromptBase):
    pass

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
        from_attributes = True # Pydantic V2 name for orm_mode