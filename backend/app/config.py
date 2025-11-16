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
    APP_ENV: str = "development"
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
    REDIS_KEY_PREFIX: str = "job-portal"

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

    # OpenAI / LangChain
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_JOB_SEEKER_MODEL: str | None = None
    OPENAI_EMPLOYER_MODEL: str | None = None
    OPENAI_SUMMARY_MODEL: str | None = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    LANGCHAIN_TRACING_ENABLED: bool = False
    LANGCHAIN_PROJECT: str | None = None

    # Conversational agent settings
    CHAT_SESSION_TTL_SECONDS: int = 60 * 60 * 48  # 48 hours
    CHAT_RECENT_MESSAGE_LIMIT: int = 20
    CHAT_SUMMARY_MAX_TOKENS: int = 750
    CHAT_RATE_LIMIT_MAX_MESSAGES: int = 30
    CHAT_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), case_sensitive=True, extra="ignore")


settings = Settings()
