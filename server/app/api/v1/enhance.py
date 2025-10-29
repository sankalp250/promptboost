from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas import prompt as schemas
from app.graphs.enhance_graph import enhancement_graph

router = APIRouter()

# Dependency to get a DB session
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
    """
    Receives a prompt, runs it through the enhancement graph, and returns the result.
    """
    inputs = {
        "original_prompt": request.original_prompt,
        "db": db
    }
    
    # Invoke the compiled LangGraph
    final_state = enhancement_graph.invoke(inputs)

    return schemas.PromptEnhanceResponse(
        original_prompt=request.original_prompt,
        enhanced_prompt=final_state.get("enhanced_prompt", "Error: Enhancement failed."),
        from_cache=final_state.get("from_cache", False)
    )