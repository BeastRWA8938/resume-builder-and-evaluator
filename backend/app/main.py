import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.app.config import validate_config
from backend.app.database import init_db
from backend.app.routes import analyze, history, generator, vault

# Initialize database
init_db()

# Validate Gemini configurations
validate_config()

app = FastAPI(
    title="ATS Resume Analyzer API",
    description="Backend API for parsing and evaluating resumes against job descriptions.",
    version="1.0.0"
)

# Configure CORS - allows strict origin checks in production
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",")] if allowed_origins_raw != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular Routers
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(generator.router)
app.include_router(vault.router)

# Setup Frontend static directories dynamically if they exist
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# Ensure directories exist so FastAPI doesn't crash on startup
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "assets").mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount resumes static directory
RESUMES_DIR = Path(__file__).resolve().parent.parent.parent / "Resumes"
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/resumes", StaticFiles(directory=str(RESUMES_DIR)), name="resumes")

@app.get("/")
async def serve_frontend():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "FastAPI ATS Backend is running. Frontend index.html not found yet."}
