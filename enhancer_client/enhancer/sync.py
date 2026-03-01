import os
import requests
import uuid
import logging
from typing import List, Dict, Tuple
from pathlib import Path

import sys
from pathlib import Path

# Add project root to sys.path
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from enhancer_client.enhancer.config import settings

logger = logging.getLogger(__name__)

# Basic files to ignore during sync
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'node_modules', '.idea', '.vscode', 'dist', 'build'}
IGNORE_EXTS = {'.exe', '.dll', '.so', '.pyc', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}

def chunk_text(text: str, filename: str, chunk_size=1000, overlap=200) -> List[Tuple[str, Dict, str]]:
    """
    Splits long text into overlapping chunks, returning a list of tuples:
    (chunk_text, metadata_dict, unique_id)
    """
    chunks = []
    text_len = len(text)
    
    # If file is empty, skip
    if text_len == 0:
        return chunks
        
    start = 0
    chunk_index = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        
        # Determine metadata
        metadata = {
            "filename": filename,
            "chunk_index": chunk_index
        }
        
        # Generate a unique ID for this chunk
        chunk_id = f"{filename}_{chunk_index}_{uuid.uuid4().hex[:8]}"
        
        chunks.append((chunk, metadata, chunk_id))
        
        start += (chunk_size - overlap)
        chunk_index += 1
        
    return chunks

def extract_project_id(workspace_path: str) -> str:
    """Consistently hashes the workspace path into a project ID (matches server logic)"""
    import hashlib
    normalized = workspace_path.strip().lower().replace("\\", "/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]

def sync_workspace_to_server(workspace_path: str | None = None):
    """
    Walks the workspace folder, chunks the files, and sends them to the server
    for Vector RAG processing.
    """
    path_to_sync = workspace_path or settings.WORKSPACE_PATH
    if not path_to_sync or not os.path.exists(path_to_sync):
        logger.error(f"Cannot sync: Workspace path '{path_to_sync}' is invalid or missing.")
        return False
        
    logger.info(f"Starting workspace sync for: {path_to_sync}")
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    root_path = Path(path_to_sync).resolve()
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in IGNORE_EXTS:
                continue
                
            file_path = Path(dirpath) / filename
            
            try:
                # Get path relative to the workspace root for better metadata reading
                rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Skip overly massive files (e.g. minified JS, giant logs) 
                if len(content) > 500_000:
                    logger.warning(f"Skipping {rel_path}: File too large (>500KB)")
                    continue
                    
                file_chunks = chunk_text(content, rel_path)
                
                for text, meta, c_id in file_chunks:
                    all_chunks.append(text)
                    all_metadatas.append(meta)
                    all_ids.append(c_id)
                    
            except Exception as e:
                logger.debug(f"Could not process file {file_path}: {e}")

    if not all_chunks:
        logger.warning("No text files found to sync.")
        return False
        
    project_id = extract_project_id(str(root_path))
    
    # Optional: Send in batches if the project is absolutely massive to avoid payload limits
    # However, FastAPI default payload limit is quite large, so sending all at once is fine for normal projects
    payload = {
        "project_id": project_id,
        "documents": all_chunks,
        "metadatas": all_metadatas,
        "ids": all_ids
    }
    
    sync_url = f"{settings.API_BASE_URL}/project/sync"
    logger.info(f"Sending {len(all_chunks)} chunks to {sync_url} for project {project_id}...")
    
    try:
        response = requests.post(sync_url, json=payload, timeout=30) # Short timeout since server responds immediately
        if response.status_code in (200, 202):
            logger.info(f"Sync accepted: {response.json().get('message')}")
            return True
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to sync to server: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"Server response: {e.response.text}")
        return False

if __name__ == "__main__":
    # If run directly as a script, force logging to console and execute manual sync
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    print("=" * 60)
    print("   PromptBoost Codebase Syncing Utility")
    print("=" * 60)
    
    workspace_path = settings.WORKSPACE_PATH or os.environ.get("PROMPTBOOST_WORKSPACE")
    if not workspace_path:
        print("ERROR: Workspace path not set. Please set PROMPTBOOST_WORKSPACE environment variable.")
    else:
        success = sync_workspace_to_server(workspace_path)
        if success:
            print("\n✅ Codebase synced successfully! You may now use RAG via !!e prompts.")
        else:
            print("\n❌ Codebase sync failed. Check server logs.")
