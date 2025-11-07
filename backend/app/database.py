from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis import asyncio as aioredis

from app.config import settings

# Global ChromaDB client instance
_chroma_client = None

# Global MongoDB client instance
_mongo_client: Optional[AsyncIOMotorClient] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB client."""
    global _chroma_client

    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            )
        )

    return _chroma_client


def get_collection(collection_name: str = None):
    """Get or create a ChromaDB collection."""
    client = get_chroma_client()
    collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the global MongoDB client."""
    global _mongo_client

    if _mongo_client is None:
        client_kwargs = {"uuidRepresentation": "standard"}

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


async def ping_redis() -> dict:
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
def get_users_collection():
    """Get users collection from MongoDB."""
    db = get_mongo_database()
    return db["users"]


def get_job_seeker_profiles_collection():
    """Get job_seeker_profiles collection from MongoDB."""
    db = get_mongo_database()
    return db["job_seeker_profiles"]


def get_employer_profiles_collection():
    """Get employer_profiles collection from MongoDB."""
    db = get_mongo_database()
    return db["employer_profiles"]
