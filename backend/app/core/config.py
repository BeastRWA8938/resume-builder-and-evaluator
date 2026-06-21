import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (either in project root or backend folder)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent
if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
else:
    load_dotenv(BACKEND_DIR / ".env")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BACKEND_DIR / "resume_analyzer.db"))
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")


def validate_config():
    if not GEMINI_API_KEY:
        print("[WARNING] GEMINI_API_KEY environment variable is not set. The analysis service will fail until it is provided.")
