from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings(BaseModel):
    app_name: str = Field(default=os.getenv("APP_NAME", "LegalEase"))
    company_name: str = Field(default=os.getenv("COMPANY_NAME", "LegalEase"))
    gemini_api_key: str = Field(default=os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    backend_host: str = Field(default=os.getenv("BACKEND_HOST", "127.0.0.1"))
    backend_port: int = Field(default=int(os.getenv("BACKEND_PORT", "8000")))
    backend_url: str = Field(default=os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            x.strip() for x in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:8501,http://127.0.0.1:8501"
            ).split(",") if x.strip()
        ]
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
