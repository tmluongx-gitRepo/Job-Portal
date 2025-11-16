import logging
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.config import Settings as ChromaSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from redis import asyncio as aioredis

from app.config import settings

_logger = logging.getLogger(__name__)

# Global ChromaDB client instance
_chroma_client: ClientAPI | None = None

# Global MongoDB client instance
_mongo_client: AsyncIOMotorClient | None = None


def get_chroma_client() -> ClientAPI:
    """Get or create ChromaDB client."""
    global _chroma_client

    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            ),
        )

    return _chroma_client


def get_collection(collection_name: str | None = None) -> Any:
    """Get or create a ChromaDB collection."""
    client = get_chroma_client()
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

    return client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the global MongoDB client."""
    global _mongo_client

    if _mongo_client is None:
        client_kwargs: dict[str, Any] = {"uuidRepresentation": "standard"}

        if settings.MONGO_URI.startswith("mongodb+srv"):
            client_kwargs["tls"] = True

        _mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            **client_kwargs,
        )

    return _mongo_client


def get_mongo_database() -> AsyncIOMotorDatabase:
    """Return the configured MongoDB database."""
    return get_mongo_client()[settings.MONGO_DB_NAME]


async def ping_mongo() -> bool:
    """Ping MongoDB to verify connectivity."""
    # Check if MONGO_URI is a placeholder or not configured
    if (
        not settings.MONGO_URI
        or settings.MONGO_URI == "mongodb://localhost:27017"
        or "<your mongodb" in settings.MONGO_URI.lower()
        or "your-mongodb" in settings.MONGO_URI.lower()
    ):
        raise ConnectionError(
            "MongoDB connection string not configured. "
            "Please set MONGO_URI in your .env file with your MongoDB Atlas connection string."
        )

    db = get_mongo_database()
    await db.command("ping")
    return True


def close_mongo_client() -> None:
    """Close the MongoDB client if it exists."""
    global _mongo_client

    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None


async def ping_redis() -> dict[str, str]:
    """Ping Redis to verify connectivity and get info."""
    redis = await aioredis.from_url(settings.REDIS_URL)
    try:
        # Ping to check connection
        await redis.ping()
        # Get Redis info
        info = await redis.info()
        return {
            "version": info.get("redis_version", "unknown"),
            "mode": info.get("redis_mode", "standalone"),
        }
    finally:
        await redis.aclose()  # type: ignore[attr-defined]


async def _safe_create_index(collection: AsyncIOMotorCollection, *args: Any, **kwargs: Any) -> None:
    """Create an index while tolerating failures on startup."""

    try:
        await collection.create_index(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive logging
        payload = {
            "collection": getattr(collection, "name", "unknown"),
            "index_args": repr(args),
            "index_kwargs": repr(kwargs),
        }
        if settings.DEBUG:
            _logger.exception("database.index_creation_failed", extra=payload)
        else:
            payload["error"] = str(exc)
            _logger.warning("database.index_creation_failed", extra=payload)


# MongoDB Collection Helpers
def get_users_collection() -> AsyncIOMotorCollection:
    """Get users collection from MongoDB."""
    db = get_mongo_database()
    return db["users"]


def get_job_seeker_profiles_collection() -> AsyncIOMotorCollection:
    """Get job_seeker_profiles collection from MongoDB."""
    db = get_mongo_database()
    return db["job_seeker_profiles"]


def get_employer_profiles_collection() -> AsyncIOMotorCollection:
    """Get employer_profiles collection from MongoDB."""
    db = get_mongo_database()
    return db["employer_profiles"]


def get_jobs_collection() -> AsyncIOMotorCollection:
    """Get jobs collection from MongoDB."""
    db = get_mongo_database()
    return db["jobs"]


def get_applications_collection() -> AsyncIOMotorCollection:
    """Get applications collection from MongoDB."""
    db = get_mongo_database()
    return db["applications"]


def get_recommendations_collection() -> AsyncIOMotorCollection:
    """Get recommendations collection from MongoDB."""
    db = get_mongo_database()
    return db["recommendations"]


def get_saved_jobs_collection() -> AsyncIOMotorCollection:
    """Get saved_jobs collection from MongoDB."""
    db = get_mongo_database()
    return db["saved_jobs"]


def get_resumes_collection() -> AsyncIOMotorCollection:
    """Get resumes collection from MongoDB."""
    db = get_mongo_database()
    return db["resumes"]


def get_interviews_collection() -> AsyncIOMotorCollection:
    """Get interviews collection from MongoDB."""
    db = get_mongo_database()
    return db["interviews"]


def get_chat_sessions_collection() -> AsyncIOMotorCollection:
    """Get chat_sessions collection from MongoDB."""
    db = get_mongo_database()
    return db["chat_sessions"]


def get_chat_messages_collection() -> AsyncIOMotorCollection:
    """Get chat_messages collection from MongoDB."""
    db = get_mongo_database()
    return db["chat_messages"]


async def _init_user_indexes(db: Any) -> None:
    """Initialize indexes for users and profiles."""
    # Users collection indexes
    users = db["users"]
    await _safe_create_index(users, "email", unique=True)
    await _safe_create_index(users, "account_type")
    await _safe_create_index(users, [("created_at", -1)])

    # Job Seeker Profiles collection indexes
    job_seeker_profiles = db["job_seeker_profiles"]
    await _safe_create_index(job_seeker_profiles, "user_id", unique=True)
    await _safe_create_index(job_seeker_profiles, "email")
    await _safe_create_index(job_seeker_profiles, "skills")
    await _safe_create_index(job_seeker_profiles, "location")
    await _safe_create_index(job_seeker_profiles, "experience_years")
    await _safe_create_index(job_seeker_profiles, [("updated_at", -1)])
    await _safe_create_index(
        job_seeker_profiles,
        [("skills", 1), ("location", 1), ("experience_years", 1)],
    )

    # Employer Profiles collection indexes
    employer_profiles = db["employer_profiles"]
    await _safe_create_index(employer_profiles, "user_id", unique=True)
    await _safe_create_index(employer_profiles, "company_name")
    await _safe_create_index(employer_profiles, "industry")
    await _safe_create_index(employer_profiles, "location")
    await _safe_create_index(employer_profiles, [("created_at", -1)])


async def _init_job_indexes(db: Any) -> None:
    """Initialize indexes for jobs and applications."""
    # Jobs collection indexes
    jobs = db["jobs"]
    await _safe_create_index(jobs, "posted_by")
    await _safe_create_index(jobs, "is_active")
    await _safe_create_index(jobs, "location")
    await _safe_create_index(jobs, "job_type")
    await _safe_create_index(jobs, "skills_required")
    await _safe_create_index(jobs, "industry")
    await _safe_create_index(jobs, "remote_ok")
    await _safe_create_index(jobs, [("created_at", -1)])
    await _safe_create_index(jobs, [("is_active", 1), ("created_at", -1)])
    await _safe_create_index(jobs, [("is_active", 1), ("location", 1), ("job_type", 1)])
    # Text index for full-text search on title, description, company
    await _safe_create_index(
        jobs,
        [("title", "text"), ("description", "text"), ("company", "text")],
        weights={"title": 10, "company": 5, "description": 1},
    )

    # Applications collection indexes
    applications = db["applications"]
    await _safe_create_index(applications, "job_seeker_id")
    await _safe_create_index(applications, "job_id")
    await _safe_create_index(applications, "status")
    await _safe_create_index(applications, [("applied_date", -1)])
    await _safe_create_index(
        applications,
        [("job_seeker_id", 1), ("job_id", 1)],
        unique=True,
    )  # Prevent duplicate applications
    await _safe_create_index(applications, [("job_id", 1), ("status", 1)])


async def _init_feature_indexes(db: Any) -> None:
    """Initialize indexes for recommendations, saved jobs, resumes, and interviews."""
    # Recommendations collection indexes
    recommendations = db["recommendations"]
    await _safe_create_index(recommendations, "job_seeker_id")
    await _safe_create_index(recommendations, "job_id")
    await _safe_create_index(recommendations, "status")
    await _safe_create_index(recommendations, [("created_at", -1)])
    await _safe_create_index(recommendations, [("job_seeker_id", 1), ("status", 1)])

    # Saved Jobs collection indexes
    saved_jobs = db["saved_jobs"]
    await _safe_create_index(saved_jobs, "job_seeker_id")
    await _safe_create_index(saved_jobs, "job_id")
    await _safe_create_index(saved_jobs, [("saved_date", -1)])
    await _safe_create_index(
        saved_jobs,
        [("job_seeker_id", 1), ("job_id", 1)],
        unique=True,
    )  # Prevent duplicate saves

    # Resumes collection indexes
    resumes = db["resumes"]
    await _safe_create_index(resumes, "job_seeker_id", unique=True)  # One resume per user
    await _safe_create_index(resumes, [("uploaded_at", -1)])

    # Interviews collection indexes
    interviews = db["interviews"]
    # One active interview per application (not historical)
    # This enforces that rescheduled interviews update the same document
    # If you need interview history, consider a separate interviews_history collection
    await _safe_create_index(interviews, "application_id", unique=True)
    await _safe_create_index(interviews, "job_id")
    await _safe_create_index(interviews, "job_seeker_id")
    await _safe_create_index(interviews, "employer_id")
    await _safe_create_index(interviews, "status")
    await _safe_create_index(interviews, [("scheduled_date", 1)])  # For upcoming interviews
    await _safe_create_index(interviews, [("created_at", -1)])
    await _safe_create_index(interviews, [("employer_id", 1), ("status", 1)])  # Employer filtering
    await _safe_create_index(
        interviews, [("job_seeker_id", 1), ("status", 1)]
    )  # Job seeker filtering


async def _init_chat_indexes(db: Any) -> None:
    """Initialize indexes for chat sessions and messages."""

    chat_sessions = db["chat_sessions"]
    await _safe_create_index(chat_sessions, "session_id", unique=True)
    await _safe_create_index(chat_sessions, "user_id")
    await _safe_create_index(chat_sessions, [("user_id", 1), ("status", 1)])
    await _safe_create_index(chat_sessions, [("last_interaction_at", -1)])

    chat_messages = db["chat_messages"]
    await _safe_create_index(chat_messages, "session_id")
    await _safe_create_index(chat_messages, [("session_id", 1), ("created_at", -1)])


async def init_db_indexes() -> None:
    """Initialize all database indexes."""
    db = get_mongo_database()
    await _init_user_indexes(db)
    await _init_job_indexes(db)
    await _init_feature_indexes(db)
    await _init_chat_indexes(db)
