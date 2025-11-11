"""
CRUD operations for interviews.
"""

from datetime import UTC, datetime
from typing import Any, cast

from bson import ObjectId
from pymongo import ReturnDocument

from app.database import get_interviews_collection
from app.type_definitions import InterviewDocument


async def create_interview(
    application_id: str,
    job_id: str,
    job_seeker_id: str,
    employer_id: str,
    interview_type: str,
    scheduled_date: datetime,
    duration_minutes: int,
    timezone: str,
    location: str | None = None,
    interviewer_name: str | None = None,
    interviewer_email: str | None = None,
    interviewer_phone: str | None = None,
    notes: str | None = None,
    internal_notes: str | None = None,
) -> InterviewDocument:
    """
    Create a new interview.

    Args:
        application_id: Application ID
        job_id: Job ID
        job_seeker_id: Job seeker profile ID
        employer_id: Employer user ID
        interview_type: Type of interview
        scheduled_date: Scheduled date and time
        duration_minutes: Duration in minutes
        timezone: Timezone
        location: Physical address or meeting link
        interviewer_name: Interviewer's name
        interviewer_email: Interviewer's email
        interviewer_phone: Interviewer's phone
        notes: Notes visible to job seeker
        internal_notes: Internal notes (employer only)

    Returns:
        Created interview document
    """
    collection = get_interviews_collection()

    interview_data: dict[str, Any] = {
        "_id": ObjectId(),
        "application_id": application_id,
        "job_id": job_id,
        "job_seeker_id": job_seeker_id,
        "employer_id": employer_id,
        "interview_type": interview_type,
        "scheduled_date": scheduled_date,
        "duration_minutes": duration_minutes,
        "timezone": timezone,
        "status": "scheduled",
        "reminder_sent": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }

    # Add optional fields
    if location:
        interview_data["location"] = location
    if interviewer_name:
        interview_data["interviewer_name"] = interviewer_name
    if interviewer_email:
        interview_data["interviewer_email"] = interviewer_email
    if interviewer_phone:
        interview_data["interviewer_phone"] = interviewer_phone
    if notes:
        interview_data["notes"] = notes
    if internal_notes:
        interview_data["internal_notes"] = internal_notes

    await collection.insert_one(interview_data)
    return cast(InterviewDocument, interview_data)


async def get_interview_by_id(interview_id: str) -> InterviewDocument | None:
    """
    Get interview by ID.

    Args:
        interview_id: Interview ID

    Returns:
        Interview document if found, None otherwise
    """
    collection = get_interviews_collection()

    try:
        return await collection.find_one({"_id": ObjectId(interview_id)})  # type: ignore[return-value]
    except Exception:
        return None


async def get_interview_by_application_id(application_id: str) -> InterviewDocument | None:
    """
    Get interview by application ID.

    Args:
        application_id: Application ID

    Returns:
        Interview document if found, None otherwise
    """
    collection = get_interviews_collection()
    return await collection.find_one({"application_id": application_id})  # type: ignore[return-value]


async def get_interviews(
    skip: int = 0,
    limit: int = 100,
    job_seeker_id: str | None = None,
    employer_id: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
    upcoming_only: bool = False,
) -> list[InterviewDocument]:
    """
    Get interviews with optional filters.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        job_seeker_id: Filter by job seeker ID
        employer_id: Filter by employer ID
        job_id: Filter by job ID
        status: Filter by status
        upcoming_only: Only return upcoming interviews

    Returns:
        List of interview documents
    """
    collection = get_interviews_collection()

    query: dict[str, Any] = {}
    if job_seeker_id:
        query["job_seeker_id"] = job_seeker_id
    if employer_id:
        query["employer_id"] = employer_id
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status
    if upcoming_only:
        query["scheduled_date"] = {"$gt": datetime.now(UTC)}
        query["status"] = {"$in": ["scheduled", "rescheduled"]}

    cursor = collection.find(query).sort("scheduled_date", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)  # type: ignore[return-value]


async def update_interview(
    interview_id: str, update_data: dict[str, Any]
) -> InterviewDocument | None:
    """
    Update an interview.

    Args:
        interview_id: Interview ID
        update_data: Dictionary of fields to update

    Returns:
        Updated interview document if found, None otherwise
    """
    collection = get_interviews_collection()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.now(UTC)

    # If scheduled_date is being changed, mark as rescheduled
    if "scheduled_date" in update_data:
        # Get current interview to save original date
        current_interview = await get_interview_by_id(interview_id)
        if current_interview and current_interview.get("status") == "scheduled":
            update_data["status"] = "rescheduled"
            update_data["rescheduled_from"] = current_interview["scheduled_date"]

    try:
        updated_interview = await collection.find_one_and_update(
            {"_id": ObjectId(interview_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        return cast(InterviewDocument, updated_interview) if updated_interview else None
    except Exception:
        return None


async def cancel_interview(
    interview_id: str, cancelled_by: str, reason: str
) -> InterviewDocument | None:
    """
    Cancel an interview.

    Args:
        interview_id: Interview ID
        cancelled_by: User ID who cancelled
        reason: Cancellation reason

    Returns:
        Updated interview document if found, None otherwise
    """
    update_data = {
        "status": "cancelled",
        "cancelled_by": cancelled_by,
        "cancelled_reason": reason,
        "updated_at": datetime.now(UTC),
    }

    return await update_interview(interview_id, update_data)


async def complete_interview(
    interview_id: str, feedback: str | None = None, rating: int | None = None
) -> InterviewDocument | None:
    """
    Mark an interview as complete.

    Args:
        interview_id: Interview ID
        feedback: Interview feedback
        rating: Rating (1-5)

    Returns:
        Updated interview document if found, None otherwise
    """
    update_data: dict[str, Any] = {
        "status": "completed",
        "updated_at": datetime.now(UTC),
    }

    if feedback:
        update_data["feedback"] = feedback
    if rating:
        update_data["rating"] = rating

    return await update_interview(interview_id, update_data)


async def count_interviews(
    job_seeker_id: str | None = None,
    employer_id: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
) -> int:
    """
    Count interviews with optional filters.

    Args:
        job_seeker_id: Filter by job seeker ID
        employer_id: Filter by employer ID
        job_id: Filter by job ID
        status: Filter by status

    Returns:
        Count of interviews
    """
    collection = get_interviews_collection()

    query: dict[str, Any] = {}
    if job_seeker_id:
        query["job_seeker_id"] = job_seeker_id
    if employer_id:
        query["employer_id"] = employer_id
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status

    return await collection.count_documents(query)


async def delete_interview(interview_id: str) -> bool:
    """
    Delete an interview.

    Args:
        interview_id: Interview ID

    Returns:
        True if deleted, False if not found
    """
    collection = get_interviews_collection()

    try:
        result = await collection.delete_one({"_id": ObjectId(interview_id)})
    except Exception:
        return False
    else:
        return result.deleted_count > 0


async def delete_interviews_by_application_id(application_id: str) -> int:
    """
    Delete all interviews for an application (cascade delete).

    Args:
        application_id: Application ID

    Returns:
        Number of interviews deleted
    """
    collection = get_interviews_collection()

    result = await collection.delete_many({"application_id": application_id})
    return result.deleted_count


async def delete_interviews_by_job_id(job_id: str) -> int:
    """
    Delete all interviews for a job (cascade delete).

    Args:
        job_id: Job ID

    Returns:
        Number of interviews deleted
    """
    collection = get_interviews_collection()

    result = await collection.delete_many({"job_id": job_id})
    return result.deleted_count
