"""
CRUD operations for saved jobs.
"""

from datetime import UTC, datetime
from typing import cast

from bson import ObjectId

from app.database import get_jobs_collection, get_saved_jobs_collection
from app.type_definitions import SavedJobDocument


async def create_saved_job(
    job_seeker_id: str, job_id: str, notes: str | None = None
) -> SavedJobDocument:
    """
    Create a new saved job.

    Args:
        job_seeker_id: ID of the job seeker saving the job
        job_id: ID of the job to save
        notes: Optional notes about why the job was saved

    Returns:
        The created saved job document

    Raises:
        ValueError: If the job doesn't exist or is already saved
    """
    saved_jobs = get_saved_jobs_collection()
    jobs = get_jobs_collection()

    # Check if job exists
    job = await jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise ValueError(f"Job with id {job_id} not found")

    # Check if already saved
    existing = await saved_jobs.find_one({"job_seeker_id": job_seeker_id, "job_id": job_id})
    if existing:
        raise ValueError("Job is already saved")

    # Create saved job
    now = datetime.now(UTC)
    saved_job_data = {
        "job_seeker_id": job_seeker_id,
        "job_id": job_id,
        "notes": notes,
        "saved_date": now,
        "created_at": now,
    }

    result = await saved_jobs.insert_one(saved_job_data)
    saved_job_data["_id"] = result.inserted_id

    return cast(SavedJobDocument, saved_job_data)


async def get_saved_jobs(
    job_seeker_id: str, skip: int = 0, limit: int = 100, include_deleted_jobs: bool = False
) -> list[SavedJobDocument]:
    """
    Get all saved jobs for a job seeker.

    Args:
        job_seeker_id: ID of the job seeker
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        include_deleted_jobs: If False, filters out saved jobs where the job no longer exists

    Returns:
        List of saved job documents
    """
    saved_jobs = get_saved_jobs_collection()

    cursor = (
        saved_jobs.find({"job_seeker_id": job_seeker_id})
        .sort("saved_date", -1)
        .skip(skip)
        .limit(limit)
    )

    saved_jobs_list = await cursor.to_list(length=limit)

    # Auto-cleanup: Remove saved jobs where the job no longer exists
    if not include_deleted_jobs:
        jobs = get_jobs_collection()
        valid_saved_jobs: list[SavedJobDocument] = []

        for saved_job in saved_jobs_list:
            job_exists = await jobs.find_one({"_id": ObjectId(saved_job["job_id"])})
            if job_exists:
                valid_saved_jobs.append(cast(SavedJobDocument, saved_job))
            else:
                # Silently remove orphaned saved job
                await saved_jobs.delete_one({"_id": saved_job["_id"]})

        return valid_saved_jobs

    return [cast(SavedJobDocument, doc) for doc in saved_jobs_list]


async def get_saved_job_by_id(saved_job_id: str) -> SavedJobDocument | None:
    """
    Get a saved job by ID.

    Args:
        saved_job_id: ID of the saved job

    Returns:
        The saved job document or None if not found
    """
    saved_jobs = get_saved_jobs_collection()

    try:
        result = await saved_jobs.find_one({"_id": ObjectId(saved_job_id)})
        return cast(SavedJobDocument, result) if result else None
    except Exception:
        return None


async def check_if_job_saved(job_seeker_id: str, job_id: str) -> bool:
    """
    Check if a job is already saved by a job seeker.

    Args:
        job_seeker_id: ID of the job seeker
        job_id: ID of the job

    Returns:
        True if the job is saved, False otherwise
    """
    saved_jobs = get_saved_jobs_collection()

    saved_job = await saved_jobs.find_one({"job_seeker_id": job_seeker_id, "job_id": job_id})
    return saved_job is not None


async def update_saved_job(saved_job_id: str, update_data: dict) -> SavedJobDocument | None:
    """
    Update a saved job.

    Args:
        saved_job_id: ID of the saved job to update
        update_data: Dictionary of fields to update

    Returns:
        The updated saved job document or None if not found
    """
    saved_jobs = get_saved_jobs_collection()

    try:
        result = await saved_jobs.find_one_and_update(
            {"_id": ObjectId(saved_job_id)},
            {"$set": update_data},
            return_document=True,
        )
        return cast(SavedJobDocument, result) if result else None
    except Exception:
        return None


async def delete_saved_job(saved_job_id: str) -> bool:
    """
    Delete a saved job.

    Args:
        saved_job_id: ID of the saved job to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    saved_jobs = get_saved_jobs_collection()

    try:
        result = await saved_jobs.delete_one({"_id": ObjectId(saved_job_id)})
    except Exception:
        return False
    else:
        return result.deleted_count > 0


async def count_saved_jobs(job_seeker_id: str) -> int:
    """
    Count the number of saved jobs for a job seeker.

    Args:
        job_seeker_id: ID of the job seeker

    Returns:
        Number of saved jobs
    """
    saved_jobs = get_saved_jobs_collection()
    return await saved_jobs.count_documents({"job_seeker_id": job_seeker_id})
