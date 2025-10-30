from sqlalchemy.orm import Session
from app.models import prompt as models
from app.schemas import prompt as schemas

def get_prompt_by_original_text(db: Session, original_prompt: str) -> models.PromptCache | None:
    """
    Retrieve a cached prompt from the database by its original text.
    """
    return db.query(models.PromptCache).filter(models.PromptCache.original_prompt == original_prompt).first()

# --- SLIGHT MODIFICATION HERE: MAKE IT RETURN THE CREATED OBJECT ---
def create_cached_prompt(db: Session, prompt: schemas.PromptCacheCreate) -> models.PromptCache:
    """
    Create a new prompt cache entry in the database.
    """
    db_prompt = models.PromptCache(
        original_prompt=prompt.original_prompt,
        enhanced_prompt=prompt.enhanced_prompt
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt # <-- Return the new object with its ID

# --- NEW CRUD FUNCTION FOR ANALYTICS ---
def create_usage_analytics_entry(db: Session, analytics_data: schemas.UsageAnalyticsCreate) -> models.UsageAnalytics:
    """
    Creates a new entry in the usage_analytics table.
    """
    db_analytics = models.UsageAnalytics(**analytics_data.model_dump())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics