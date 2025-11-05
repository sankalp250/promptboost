from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1 import enhance as enhance_api, feedback as feedback_api
from app.core.config import settings
from app.services import ml_inference_service # <-- Import our new service

# --- NEW: Use FastAPI's modern lifespan event handler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("--- Server Starting Up ---")
    ml_inference_service.load_ml_models()
    yield
    # This code runs on shutdown
    print("--- Server Shutting Down ---")


# Pass the lifespan manager to the FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan # <-- Add this line
)

# Add CORS middleware to allow cross-origin requests
# This is useful if you want to use the API from web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (unchanged)
app.include_router(enhance_api.router, prefix="/api/v1", tags=["enhancement"])
app.include_router(feedback_api.router, prefix="/api/v1", tags=["feedback"])

# Health Check (unchanged)
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}