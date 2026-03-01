import hashlib
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas import prompt as schemas
from app.graphs.enhance_graph import enhancement_graph
from app.crud import prompt_cache as crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def resolve_project_id(workspace_path: str | None, project_id: str | None) -> str | None:
    """Resolve project_id: use request project_id if set, else derive from workspace_path."""
    if project_id:
        return project_id
    if not workspace_path or not workspace_path.strip():
        return None
    normalized = workspace_path.strip().lower().replace("\\", "/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]


@router.post("/enhance", response_model=schemas.PromptEnhanceResponse)
def enhance_prompt_endpoint(
    request: schemas.PromptEnhanceRequest,
    db: Session = Depends(get_db)
):
    project_id = resolve_project_id(request.workspace_path, request.project_id)
    recent_prompts: list[tuple[str, str]] = []
    if project_id:
        recent_prompts = crud.get_recent_prompts_for_project(
            db, project_id=project_id, user_id=request.user_id, limit=5
        )
    # NEW: Fetch similar chunks from Vector DB
    from app.services.vector_db import vector_db
    rag_context = ""
    if project_id:
        rag_context = vector_db.query_project_context(project_id, request.original_prompt, n_results=5)
    
    # Combine static context with RAG context
    full_project_context = request.project_context or ""
    if rag_context:
        full_project_context += f"\n\n--- Relevant Code Snippets from Repository ---\n{rag_context}"
    
    inputs = {
        "original_prompt": request.true_original_prompt if request.is_reroll and request.true_original_prompt else request.original_prompt,
        "user_id": request.user_id,
        "session_id": request.session_id,
        "db": db,
        "is_reroll": request.is_reroll,
        "previous_enhancement": request.original_prompt if request.is_reroll else None,
        "project_id": project_id,
        "project_context": full_project_context if full_project_context else None,
        "recent_prompts": recent_prompts,
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