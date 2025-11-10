from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.config import Settings as ChromaSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from redis import asyncio as aioredis

from app.config import settings

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
        await redis.aclose()


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


async def init_db_indexes() -> None:
    """Initialize all database indexes."""
    db = get_mongo_database()

    # Users collection indexes
    users = db["users"]
    await users.create_index("email", unique=True)
    await users.create_index("account_type")
    await users.create_index([("created_at", -1)])

    # Job Seeker Profiles collection indexes
    job_seeker_profiles = db["job_seeker_profiles"]
    await job_seeker_profiles.create_index("user_id", unique=True)
    await job_seeker_profiles.create_index("email")
    await job_seeker_profiles.create_index("skills")
    await job_seeker_profiles.create_index("location")
    await job_seeker_profiles.create_index("experience_years")
    await job_seeker_profiles.create_index([("updated_at", -1)])
    await job_seeker_profiles.create_index([
        ("skills", 1),
        ("location", 1),
        ("experience_years", 1)
    ])

    # Employer Profiles collection indexes
    employer_profiles = db["employer_profiles"]
    await employer_profiles.create_index("user_id", unique=True)
    await employer_profiles.create_index("company_name")
    await employer_profiles.create_index("industry")
    await employer_profiles.create_index("location")
    await employer_profiles.create_index([("created_at", -1)])

    # Jobs collection indexes
    jobs = db["jobs"]
    await jobs.create_index("posted_by")
    await jobs.create_index("is_active")
    await jobs.create_index("location")
    await jobs.create_index("job_type")
    await jobs.create_index("skills_required")
    await jobs.create_index("industry")
    await jobs.create_index("remote_ok")
    await jobs.create_index([("created_at", -1)])
    await jobs.create_index([
        ("is_active", 1),
        ("created_at", -1)
    ])
    await jobs.create_index([
        ("is_active", 1),
        ("location", 1),
        ("job_type", 1)
    ])
    # Text index for full-text search on title, description, company
    await jobs.create_index([
        ("title", "text"),
        ("description", "text"),
        ("company", "text")
    ], weights={"title": 10, "company": 5, "description": 1})

    # Applications collection indexes
    applications = db["applications"]
    await applications.create_index("job_seeker_id")
    await applications.create_index("job_id")
    await applications.create_index("status")
    await applications.create_index([("applied_date", -1)])
    await applications.create_index([
        ("job_seeker_id", 1),
        ("job_id", 1)
    ], unique=True)  # Prevent duplicate applications
    await applications.create_index([
        ("job_id", 1),
        ("status", 1)
    ])

    # Recommendations collection indexes
    recommendations = db["recommendations"]
    await recommendations.create_index("job_seeker_id")
    await recommendations.create_index("job_id")
    await recommendations.create_index("status")
    await recommendations.create_index([("created_at", -1)])
    await recommendations.create_index([
        ("job_seeker_id", 1),
        ("status", 1)
    ])

