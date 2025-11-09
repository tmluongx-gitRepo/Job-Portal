from contextlib import asynccontextmanager


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, users, job_seeker_profiles, employer_profiles, jobs, applications, recommendations
from app.config import settings
from app.database import close_mongo_client, get_chroma_client, ping_mongo, ping_redis


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize ChromaDB connection
    try:
        client = get_chroma_client()
        print(f"✅ Connected to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
        print(f"✅ ChromaDB heartbeat: {client.heartbeat()}")
    except Exception as e:
        error_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
        print(f"⚠️  Failed to connect to ChromaDB: {error_msg}")

    # Initialize MongoDB connection
    try:
        await ping_mongo()
        print("✅ Connected to MongoDB")
    except ConnectionError as e:
        # User-friendly error for configuration issues
        print(f"⚠️  MongoDB: {e}")
    except Exception as e:
        # Network or other connection errors
        error_msg = str(e).split(",")[0] if "," in str(e) else str(e)
        print(f"⚠️  Failed to connect to MongoDB: {error_msg}")

    # Initialize Redis connection
    try:
        redis_info = await ping_redis()
        print(f"✅ Connected to Redis at {settings.REDIS_URL}")
        print(f"✅ Redis version: {redis_info['version']} ({redis_info['mode']})")
    except ConnectionError as e:
        # User-friendly error for configuration issues
        print(f"⚠️  Redis: {e}")
    except Exception as e:
        # Network or other connection errors
        error_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
        print(f"⚠️  Failed to connect to Redis: {error_msg}")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")

    close_mongo_client()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A full-stack job portal application API",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(job_seeker_profiles.router, prefix="/api/job-seeker-profiles", tags=["Job Seeker Profiles"])
app.include_router(employer_profiles.router, prefix="/api/employer-profiles", tags=["Employer Profiles"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
