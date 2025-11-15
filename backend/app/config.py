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
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase Authentication
    # TEMPORARY: Hardcoded until backend config fix is applied (see BACKEND_CONFIG_FIX.md)
    # TODO: Remove hardcoded values after backend devs fix environment variable loading
    SUPABASE_URL: str = "https://zoqyyuootjvzjlkrbqtp.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvcXl5dW9vdGp2empsa3JicXRwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2OTg5ODMsImV4cCI6MjA3ODI3NDk4M30.9wcmfi3a4VsfhOTeGSVZrDzbmCUAmbVtwxXgdR0Rxm0"
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvcXl5dW9vdGp2empsa3JicXRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjY5ODk4MywiZXhwIjoyMDc4Mjc0OTgzfQ.rgPWo_-v9OCmbl1qAXcc9NR9bcbVwSdar9I9mDGPhZw"  # For testing/admin operations
    SUPABASE_JWT_SECRET: str = "2wZBIFtSb0bAbIUrTaz3KRIreWPkTOEjTWlLFmpzE3sg7xKT//M1H3cTQ5lQa904tkZ7XdCNIiZktlUzdeTWZw=="  # For JWT signature verification

    # Dropbox File Storage
    DROPBOX_APP_KEY: str = ""
    DROPBOX_APP_SECRET: str = ""
    DROPBOX_ACCESS_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), case_sensitive=True, extra="ignore")


settings = Settings()
