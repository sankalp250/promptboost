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

@router.post("/enhance", response_model=schemas.PromptEnhanceResponse)
def enhance_prompt_endpoint(
    request: schemas.PromptEnhanceRequest,
    db: Session = Depends(get_db)
):
    inputs = {
        "original_prompt": request.true_original_prompt if request.is_reroll and request.true_original_prompt else request.original_prompt,
        "user_id": request.user_id,
        "session_id": request.session_id,
        "db": db,
        "is_reroll": request.is_reroll,
        "previous_enhancement": request.original_prompt if request.is_reroll else None
    }
    
    try:
        final_state = enhancement_graph.invoke(inputs)
        enhanced = final_state.get("enhanced_prompt")
        
        # Ensure enhanced_prompt is never None for Pydantic validation
        if enhanced is None or not isinstance(enhanced, str):
            enhanced = "Error: Enhancement failed on the server. Please check server logs."
        
        return schemas.PromptEnhanceResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=enhanced,
            from_cache=final_state.get("from_cache", False)
        )
    except Exception as e:
        print(f"/enhance failed: {e}")
        return schemas.PromptEnhanceResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=f"Error: Enhancement failed - {str(e)}",
            from_cache=False
        )