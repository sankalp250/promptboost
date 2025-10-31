from fastapi import FastAPI
from app.api.v1 import enhance as enhance_api
from app.api.v1 import feedback as feedback_api
from app.core.config import settings

# Create the FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="0.1.0"
)

# Include the API routers
app.include_router(enhance_api.router, prefix="/api/v1", tags=["enhancement"])
app.include_router(feedback_api.router, prefix="/api/v1", tags=["feedback"])

# Add a simple health check endpoint
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}