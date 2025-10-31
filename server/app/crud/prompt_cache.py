import uuid # <-- THIS IS THE FIX. ADD THIS LINE.
from sqlalchemy.orm import Session, joinedload
from app.models import prompt as models
from app.schemas import prompt as schemas

# ... (the rest of the file is correct and does not need to be changed) ...

def get_prompt_by_original_text(db: Session, original_prompt: str) -> models.UsageAnalytics | None:
    """
    Retrieve a cached prompt from the database by its original text.
    """
    return db.query(models.PromptCache).filter(models.PromptCache.original_prompt == original_prompt).first()


def create_cached_prompt(db: Session, prompt: schemas.PromptCacheCreate) -> models.PromptCache:
    """
    Create a new prompt cache entry in the database.
    """
    db_prompt = models.Prompt-ache(
        original_prompt=prompt.original_prompt,
        enhanced_prompt=prompt.enhanced_prompt
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt # <-- Return the new object with its ID

def create_usage_analytics_entry(db: Session, analytics_data: schemas.UsageAnalyticsCreate) -> models.UsageAnalytics:
    """
    Creates a new entry in the usage_analytics table.
    """
    db_analytics = models.UsageAnalytics(**analytics_data.model_dump())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

def update_user_action_for_session(db: Session, session_id: uuid.UUID, user_action: models.UserAction) -> models.UsageAnalytics | None:
    """
    Finds a usage_analytics entry by session_id and updates its user_action.
    """
    # Find the most recent entry for this session ID
    db_analytics = db.query(models.UsageAnalytics).filter(models.UsageAnalytics.session_id == session_id).order_by(models.UsageAnalytics.created_at.desc()).first()

    if db_analytics:
        db_analytics.user_action = user_action
        db.commit()
        db.refresh(db_analytics)
        return db_analytics
    
    return None # Return None if no entry was found for that session