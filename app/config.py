from pathlib import Path
from dotenv import load_dotenv
import os
import secrets

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
    IS_RENDER = os.getenv("RENDER", "").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
    APP_TITLE = "Bilim Al"
    APP_VERSION = "2.0.0"
    DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{PROJECT_ROOT / 'ai_tutor.db'}"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
    ENABLE_CODE_EXECUTION = os.getenv("ENABLE_CODE_EXECUTION", "false").lower() == "true"

settings = Settings()
if settings.IS_RENDER:
    if settings.ENABLE_CODE_EXECUTION:
        raise RuntimeError("Unisolated code execution must be disabled on Render")
    if not os.getenv("SECRET_KEY") or settings.SECRET_KEY == "supersecretkey":
        raise RuntimeError("Set a unique SECRET_KEY in Render environment variables")
    if settings.DATABASE_URL.startswith("sqlite:"):
        raise RuntimeError("Set DATABASE_URL to a persistent PostgreSQL database on Render")
