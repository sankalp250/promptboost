from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas import prompt as schemas
from app.graphs.enhance_graph import enhancement_graph

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- UPDATED ENDPOINT ---
@router.post("/enhance", response_model=schemas.PromptEnhanceResponse)
def enhance_prompt_endpoint(
    # The request body now expects the updated schema
    request: schemas.PromptEnhanceRequest,
    db: Session = Depends(get_db)
):
    """
    Receives a prompt with user/session IDs, runs it through the 
    enhancement graph with A/B testing, and returns the result.
    """
    # The initial state for our graph now includes user and session IDs
    inputs = {
        "original_prompt": request.original_prompt,
        "user_id": request.user_id,
        "session_id": request.session_id,
        "db": db
    }
    
    final_state = enhancement_graph.invoke(inputs)

    return schemas.PromptEnhanceResponse(
        original_prompt=request.original_prompt,
        enhanced_prompt=final_state.get("enhanced_prompt", "Error: Enhancement failed."),
        from_cache=final_state.get("from_cache", False)
    )