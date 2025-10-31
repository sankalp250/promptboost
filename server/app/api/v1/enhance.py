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
    
    try:
        final_state = enhancement_graph.invoke(inputs)
        enhanced = final_state.get("enhanced_prompt")
        return schemas.PromptEnhanceResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=enhanced if isinstance(enhanced, str) and enhanced else "Error: Enhancement failed.",
            from_cache=final_state.get("from_cache", False)
        )
    except Exception as e:
        # Prevent 500s from bubbling to the client; log and return a safe payload
        # Note: FastAPI will still produce 200 here with an error message body to keep the client resilient
        print(f"/enhance failed: {e}")
        return schemas.PromptEnhanceResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt="Error: Enhancement failed.",
            from_cache=False
        )