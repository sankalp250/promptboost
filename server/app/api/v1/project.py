from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.vector_db import vector_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChunkSyncRequest(BaseModel):
    project_id: str
    documents: list[str]
    metadatas: list[dict]
    ids: list[str]

def _run_sync_in_background(project_id: str, documents: list, metadatas: list, ids: list):
    """
    This function runs in a background thread, embedding and storing all chunks.
    It decouples heavy embedding work from the HTTP request lifecycle.
    """
    try:
        logger.info(f"Background sync starting for project {project_id} — {len(documents)} chunks.")
        vector_db.upsert_project_documents(
            project_id=project_id,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Background sync complete for project {project_id}.")
    except Exception as e:
        logger.error(f"Background sync FAILED for project {project_id}: {e}")

@router.post("/project/sync", status_code=202)
def sync_project_chunks(request: ChunkSyncRequest, background_tasks: BackgroundTasks):
    """
    Immediately returns 202 Accepted and processes the codebase chunking in the background.
    This prevents the client from timing out while waiting for ~500 Gemini API calls.
    """
    if not vector_db.is_ready():
        raise HTTPException(status_code=503, detail="Vector DB service is not initialized.")
    
    background_tasks.add_task(
        _run_sync_in_background,
        project_id=request.project_id,
        documents=request.documents,
        metadatas=request.metadatas,
        ids=request.ids
    )
    return {"status": "accepted", "message": f"Sync of {len(request.documents)} chunks for project {request.project_id} has started in the background."}
