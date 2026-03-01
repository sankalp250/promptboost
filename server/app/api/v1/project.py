from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile, Form
from pydantic import BaseModel
from app.services.vector_db import vector_db
import logging
import zipfile
import io
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# Basic files to ignore during ZIP sync
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'node_modules', '.idea', '.vscode', 'dist', 'build'}
IGNORE_EXTS = {'.exe', '.dll', '.so', '.pyc', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}

def chunk_text(text: str, filename: str, chunk_size=1000, overlap=200):
    chunks = []
    text_len = len(text)
    if text_len == 0:
        return chunks
    start = 0
    chunk_index = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append((
            text[start:end],
            {"filename": filename, "chunk_index": chunk_index},
            f"{filename}_{chunk_index}_{uuid.uuid4().hex[:8]}"
        ))
        start += (chunk_size - overlap)
        chunk_index += 1
    return chunks

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
        if not documents:
            logger.warning(f"No documents to sync for project {project_id}")
            return
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

@router.post("/project/upload", status_code=202)
async def upload_project_zip(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Receives a ZIP file containing a codebase. Extracts it in-memory, 
    chunks all valid text files, and hands them to the background sync worker.
    """
    if not vector_db.is_ready():
        raise HTTPException(status_code=503, detail="Vector DB service is not initialized.")

    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    try:
        contents = await file.read()
        zip_buffer = io.BytesIO(contents)
        
        documents = []
        metadatas = []
        ids = []

        with zipfile.ZipFile(zip_buffer, 'r') as z:
            for file_info in z.infolist():
                if file_info.is_dir():
                    continue
                
                # Check ignores
                parts = file_info.filename.split('/')
                if any(p in IGNORE_DIRS for p in parts):
                    continue
                    
                import os
                ext = os.path.splitext(file_info.filename)[1].lower()
                if ext in IGNORE_EXTS:
                    continue
                
                # Exclude huge files
                if file_info.file_size > 500_000:
                    continue

                try:
                    with z.open(file_info) as f:
                        text_content = f.read().decode('utf-8', errors='ignore')
                        
                    file_chunks = chunk_text(text_content, file_info.filename)
                    for text, meta, c_id in file_chunks:
                        documents.append(text)
                        metadatas.append(meta)
                        ids.append(c_id)
                except Exception as e:
                    logger.debug(f"Could not read file {file_info.filename} from ZIP: {e}")

        background_tasks.add_task(
            _run_sync_in_background,
            project_id=project_id,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return {
            "status": "accepted",
            "message": f"ZIP uploaded. Extracted {len(documents)} chunks to sync in background for project {project_id}."
        }

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file.")
    except Exception as e:
        logger.error(f"Error processing ZIP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing ZIP.")
