from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env file in project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # Job-Portal/
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Job Portal API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # ChromaDB Vector Database
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "job_portal"

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "job_portal"
    MONGO_TEST_DB_NAME: str = "job_portal_test"  # Test database name

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    # Must be set via environment variable - never use default in production!
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase Authentication
    # These must be set via environment variables (.env file)
    # Never commit secrets to version control!
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""  # For testing/admin operations - NEVER commit this!
    SUPABASE_JWT_SECRET: str = ""  # For JWT signature verification - NEVER commit this!

    # Dropbox File Storage
    DROPBOX_APP_KEY: str = ""
    DROPBOX_APP_SECRET: str = ""
    DROPBOX_ACCESS_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), case_sensitive=True, extra="ignore")


settings = Settings()
