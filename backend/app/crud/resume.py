"""
CRUD operations for resumes.
"""

from datetime import UTC, datetime
from typing import cast

from bson import ObjectId
from pymongo import ReturnDocument

from app.database import get_resumes_collection
from app.type_definitions import ResumeDocument


async def create_or_update_resume(
    job_seeker_id: str, dropbox_path: str, original_filename: str, content_type: str
) -> ResumeDocument:
    """
    Create or update a resume for a job seeker.

    Args:
        job_seeker_id: ID of the job seeker
        dropbox_path: Path to file in Dropbox
        original_filename: Original filename uploaded by user
        content_type: MIME type of the file

    Returns:
        The created or updated resume document
    """
    resumes = get_resumes_collection()
    now = datetime.now(UTC)

    resume_data = {
        "job_seeker_id": job_seeker_id,
        "dropbox_path": dropbox_path,
        "original_filename": original_filename,
        "uploaded_at": now,
        "content_type": content_type,
        "updated_at": now,
    }

    # Upsert: update if exists, create if not
    result = await resumes.find_one_and_update(
        {"job_seeker_id": job_seeker_id},
        {
            "$set": resume_data,
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return cast(ResumeDocument, result)


async def get_resume_by_job_seeker(job_seeker_id: str) -> ResumeDocument | None:
    """
    Get a resume by job seeker ID.

    Args:
        job_seeker_id: ID of the job seeker

    Returns:
        The resume document or None if not found
    """
    resumes = get_resumes_collection()

    try:
        resume = await resumes.find_one({"job_seeker_id": job_seeker_id})
        return cast(ResumeDocument, resume) if resume else None
    except Exception:
        return None


async def get_resume_by_id(resume_id: str) -> ResumeDocument | None:
    """
    Get a resume by ID.

    Args:
        resume_id: ID of the resume

    Returns:
        The resume document or None if not found
    """
    resumes = get_resumes_collection()

    try:
        resume = await resumes.find_one({"_id": ObjectId(resume_id)})
        return cast(ResumeDocument, resume) if resume else None
    except Exception:
        return None


async def delete_resume(job_seeker_id: str) -> bool:
    """
    Delete a resume by job seeker ID.

    Args:
        job_seeker_id: ID of the job seeker

    Returns:
        True if deleted successfully, False otherwise
    """
    resumes = get_resumes_collection()

    try:
        result = await resumes.delete_one({"job_seeker_id": job_seeker_id})
    except Exception:
        return False
    else:
        return result.deleted_count > 0  # type: ignore[no-any-return]
