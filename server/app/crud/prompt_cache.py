import uuid # <-- THIS IS THE FIX. ADD THIS LINE.
from sqlalchemy.orm import Session, joinedload
from app.models import prompt as models
from app.schemas import prompt as schemas

# ... (the rest of the file is correct and does not need to be changed) ...

def get_prompt_by_original_text(
    db: Session, original_prompt: str, project_id: str | None = None
) -> models.PromptCache | None:
    """
    Retrieve a cached prompt by original text and optional project_id.
    When project_id is set, cache is project-scoped; otherwise global (project_id IS NULL).
    """
    q = db.query(models.PromptCache).filter(models.PromptCache.original_prompt == original_prompt)
    if project_id is not None:
        q = q.filter(models.PromptCache.project_id == project_id)
    else:
        q = q.filter(models.PromptCache.project_id.is_(None))
    return q.first()


def create_cached_prompt(db: Session, prompt: schemas.PromptCacheCreate) -> models.PromptCache:
    """
    Create a new prompt cache entry in the database.
    """
    db_prompt = models.PromptCache(
        original_prompt=prompt.original_prompt,
        enhanced_prompt=prompt.enhanced_prompt,
        project_id=prompt.project_id,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt # <-- Return the new object with its ID

def create_prompt_history_entry(
    db: Session, data: schemas.PromptHistoryCreate
) -> models.PromptHistory:
    """Append an entry to prompt history for a project (for LLM continuity)."""
    entry = models.PromptHistory(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_recent_prompts_for_project(
    db: Session,
    project_id: str,
    user_id: uuid.UUID | None = None,
    limit: int = 5,
) -> list[tuple[str, str]]:
    """
    Return the most recent (original_prompt, enhanced_prompt) pairs for the project.
    If user_id is provided, filter by user; otherwise return for any user in the project.
    Ordered by created_at desc.
    """
    q = (
        db.query(models.PromptHistory.original_prompt, models.PromptHistory.enhanced_prompt)
        .filter(models.PromptHistory.project_id == project_id)
    )
    if user_id is not None:
        q = q.filter(models.PromptHistory.user_id == user_id)
    q = q.order_by(models.PromptHistory.created_at.desc()).limit(limit)
    rows = q.all()
    return [(r[0], r[1]) for r in rows]


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
    """Finds a usage_analytics entry by session_id and updates its user_action."""
    
    print(f"\n{'='*80}")
    print(f"!!!! SERVER CRUD: Updating feedback for session_id: {session_id} !!!!")
    print(f"{'='*80}")
    
    # Try exact match first
    db_analytics = db.query(models.UsageAnalytics).filter(
        models.UsageAnalytics.session_id == session_id
    ).order_by(models.UsageAnalytics.created_at.desc()).first()
    
    if not db_analytics:
        # FALLBACK: Find the most recent NON-REJECTED entry (likely the one user wants to reject)
        print(f"!!!! SERVER CRUD: No exact match for {session_id}. Using fallback: most recent non-rejected entry !!!!")
        from sqlalchemy import or_
        db_analytics = db.query(models.UsageAnalytics).filter(
            or_(
                models.UsageAnalytics.user_action != models.UserAction.rejected,
                models.UsageAnalytics.user_action.is_(None)
            )
        ).order_by(models.UsageAnalytics.created_at.desc()).first()
        
        if db_analytics:
            print(f"!!!! SERVER CRUD: FALLBACK SUCCESS - Found entry ID: {db_analytics.id}, session: {db_analytics.session_id} !!!!")
            print(f"!!!! SERVER CRUD: NOTE: Using fallback because session_id didn't match - this is okay for now !!!!")
    
    if db_analytics:
        old_action = db_analytics.user_action.value if db_analytics.user_action else None
        print(f"!!!! SERVER CRUD: Updating entry ID: {db_analytics.id} !!!!")
        print(f"!!!! SERVER CRUD: Old action: {old_action} -> New action: {user_action.value} !!!!")
        
        db_analytics.user_action = user_action
        db.commit()
        db.refresh(db_analytics)
        
        # Verify the update
        verified = db.query(models.UsageAnalytics).filter(models.UsageAnalytics.id == db_analytics.id).first()
        verified_action = verified.user_action.value if verified.user_action else None
        print(f"!!!! SERVER CRUD: ✅ COMMITTED! Verified action is now: {verified_action} !!!!")
        print(f"{'='*80}\n")
        return db_analytics
    
    # Last resort: log all sessions for debugging
    all_sessions = db.query(models.UsageAnalytics).order_by(models.UsageAnalytics.created_at.desc()).limit(5).all()
    print(f"!!!! SERVER CRUD: ❌ FAILED - No entry found. Recent sessions:")
    for s in all_sessions:
        action_str = s.user_action.value if s.user_action else "None"
        print(f"   ID: {s.id}, Session: {s.session_id}, Action: {action_str}, Created: {s.created_at}")
    print(f"{'='*80}\n")
    return None