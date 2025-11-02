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
def record_feedback(request: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    # --- DEBUG ---
    print(f"\n\n\n!!!! SERVER ENDPOINT: /feedback endpoint HIT! Received session_id: {request.session_id}, action: {request.user_action.value} !!!!\n\n\n")
    
    updated_entry = crud.update_user_action_for_session(db=db, session_id=request.session_id, user_action=request.user_action)
    if not updated_entry:
        print(f"!!!! SERVER ENDPOINT: CRUD function reported FAILURE. Did not find session ID. !!!!")
        return schemas.FeedbackResponse(status="warning", message="Session ID not found.")
    
    print(f"!!!! SERVER ENDPOINT: CRUD function reported SUCCESS. !!!!")
    return schemas.FeedbackResponse(status="success", message="Feedback recorded.")