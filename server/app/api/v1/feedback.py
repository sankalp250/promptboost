from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas import prompt as schemas
from app.crud import prompt_cache as crud

router = APIRouter()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/feedback", response_model=schemas.FeedbackResponse)
def record_feedback(
    request: schemas.FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Receives feedback from the client about a specific enhancement session
    and updates the user_action in the database.
    """
    print(f"---FEEDBACK RECEIVED---")
    print(f"Session ID: {request.session_id}, Action: {request.user_action.value}")

    updated_entry = crud.update_user_action_for_session(
        db=db,
        session_id=request.session_id,
        user_action=request.user_action
    )

    if not updated_entry:
        print(f"Warning: No usage analytics entry found for session ID {request.session_id}")
        # We don't raise an error to the client, as this is a non-critical failure.
        # The feedback is "fire-and-forget".
        return schemas.FeedbackResponse(status="warning", message="Session ID not found, but request acknowledged.")

    return schemas.FeedbackResponse(status="success", message="Feedback recorded successfully.")