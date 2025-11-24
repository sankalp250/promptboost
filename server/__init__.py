# Ensure the 'server' directory is treatable as a top-level root when this
# package is imported (e.g., via `uvicorn server.main:app`). FastAPI modules
# inside `server/app` expect to import `app.*`, so we append the server root to
# `sys.path` at import-time if it isn't already there.
import sys
from pathlib import Path

server_root = Path(__file__).resolve().parent
if str(server_root) not in sys.path:
    sys.path.append(str(server_root))

