from fastapi import APIRouter, status
from redis import asyncio as aioredis

from app.config import settings
from app.database import ping_mongo

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the API and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mongodb": "unknown",
        "redis": "unknown",
    }

    # Check MongoDB connection
    try:
        await ping_mongo()
        health_status["mongodb"] = "healthy"
    except Exception as e:
        health_status["mongodb"] = f"unhealthy: {e!s}"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.aclose()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {e!s}"
        health_status["status"] = "degraded"

    return health_status
