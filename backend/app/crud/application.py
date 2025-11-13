from datetime import UTC, datetime
from typing import cast

from bson import ObjectId
from bson.errors import InvalidId

from app.constants import ApplicationStatus, InterviewStatus
from app.database import get_applications_collection
from app.type_definitions import ApplicationDocument


async def create_application(
    application_data: dict[str, object], job_seeker_id: str
) -> ApplicationDocument:
    """
    Create a new job application.

    Args:
        application_data: Application data dictionary
        job_seeker_id: ID of the job seeker applying

    Returns:
        Created application document
    """
    collection = get_applications_collection()

    now = datetime.now(UTC)

    # Create status history entry
    initial_status = ApplicationStatus.SUBMITTED.value
    status_history_entry = {
        "status": initial_status,
        "changed_at": now,
        "notes": "Application submitted",
        "changed_by": job_seeker_id,
    }

    application_doc = {
        **application_data,
        "job_seeker_id": job_seeker_id,
        "status": initial_status,
        "applied_date": now,
        "next_step": None,
        "interview_scheduled_date": None,
        "rejection_reason": None,
        "status_history": [status_history_entry],
        "created_at": now,
        "updated_at": now,
    }

    result = await collection.insert_one(application_doc)
    application_doc["_id"] = result.inserted_id

    return cast(ApplicationDocument, application_doc)


async def get_application_by_id(application_id: str) -> ApplicationDocument | None:
    """
    Get an application by ID.

    Args:
        application_id: Application ID

    Returns:
        Application document or None if not found
    """
    collection = get_applications_collection()

    try:
        object_id = ObjectId(application_id)
    except Exception:
        return None

    result = await collection.find_one({"_id": object_id})
    return cast(ApplicationDocument, result) if result else None


async def get_applications(
    skip: int = 0,
    limit: int = 100,
    job_seeker_id: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
) -> list[ApplicationDocument]:
    """
    Get a list of applications with optional filters.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        job_seeker_id: Filter by job seeker ID
        job_id: Filter by job ID
        status: Filter by status

    Returns:
        List of application documents
    """
    collection = get_applications_collection()

    query: dict[str, object] = {}
    if job_seeker_id:
        query["job_seeker_id"] = job_seeker_id
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status

    cursor = collection.find(query).skip(skip).limit(limit).sort("applied_date", -1)
    results = await cursor.to_list(length=limit)

    return cast(list[ApplicationDocument], results)


async def update_application(
    application_id: str, update_data: dict[str, object], changed_by: str | None = None
) -> ApplicationDocument | None:
    """
    Update an application.

    Args:
        application_id: Application ID
        update_data: Fields to update
        changed_by: User ID making the change (for status history)

    Returns:
        Updated application document or None if not found
    """
    collection = get_applications_collection()

    try:
        object_id = ObjectId(application_id)
    except Exception:
        return None

    # Get current application to check for status change
    current_app = await collection.find_one({"_id": object_id})
    if not current_app:
        return None
    current_doc = cast(ApplicationDocument, current_app)

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if not update_data:
        return current_doc

    update_data["updated_at"] = datetime.now(UTC)

    # If status is being changed, add to status history
    if "status" in update_data and update_data["status"] != current_doc.get("status"):
        new_status_entry = {
            "status": update_data["status"],
            "changed_at": datetime.now(UTC),
            "notes": update_data.get("notes", "Status changed"),
            "changed_by": changed_by or "system",
        }

        # Add to status history
        result = await collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data, "$push": {"status_history": new_status_entry}},
            return_document=True,
        )
    else:
        result = await collection.find_one_and_update(
            {"_id": object_id}, {"$set": update_data}, return_document=True
        )

    return cast(ApplicationDocument, result) if result else None


async def delete_application(application_id: str) -> bool:
    """
    Delete an application (hard delete).

    Args:
        application_id: Application ID

    Returns:
        True if deleted, False if not found
    """
    collection = get_applications_collection()

    try:
        object_id = ObjectId(application_id)
    except Exception:
        return False

    result = await collection.delete_one({"_id": object_id})
    return bool(result.deleted_count > 0)


async def get_applications_count(
    job_seeker_id: str | None = None, job_id: str | None = None, status: str | None = None
) -> int:
    """
    Get the total count of applications.

    Args:
        job_seeker_id: Filter by job seeker ID
        job_id: Filter by job ID
        status: Filter by status

    Returns:
        Total count of applications
    """
    collection = get_applications_collection()

    query: dict[str, object] = {}
    if job_seeker_id:
        query["job_seeker_id"] = job_seeker_id
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status

    return await collection.count_documents(query)


async def check_duplicate_application(job_seeker_id: str, job_id: str) -> bool:
    """
    Check if a job seeker has already applied to a job.

    Args:
        job_seeker_id: Job seeker ID
        job_id: Job ID

    Returns:
        True if duplicate exists, False otherwise
    """
    collection = get_applications_collection()

    existing = await collection.find_one({"job_seeker_id": job_seeker_id, "job_id": job_id})

    return existing is not None


async def cancel_all_interviews_for_application(application_id: str) -> int:
    """
    Cancel all scheduled/rescheduled interviews for an application.

    This is typically called when an application is rejected or accepted,
    to automatically cancel any pending interviews.

    Note:
        Race conditions: This does not prevent new interviews from being scheduled
        after cancellation. Business logic should prevent interviews for applications
        in REJECTED/ACCEPTED states.

    Args:
        application_id: Application ID

    Returns:
        Number of interviews cancelled
    """
    from app.crud import interview as interview_crud
    from app.database import get_interviews_collection

    interviews_collection = get_interviews_collection()

    # Find all scheduled or rescheduled interviews for this application
    interviews = await interviews_collection.find(
        {
            "application_id": application_id,
            "status": {"$in": [InterviewStatus.SCHEDULED.value, InterviewStatus.RESCHEDULED.value]},
        }
    ).to_list(length=100)  # Reasonable limit - most applications have 1-3 interviews

    cancelled_count = 0

    for interview in interviews:
        result = await interview_crud.cancel_interview(
            str(interview["_id"]),
            cancelled_by="system",
            reason="Application status changed",
        )
        # cancel_interview returns the updated document or None
        if result is not None:
            cancelled_count += 1

    return cancelled_count


async def reject_other_applications_for_job(job_id: str, except_application_id: str) -> int:
    """
    Auto-reject all other applications when one is accepted.

    Warning:
        This method may load a large number of documents into memory if a job has
        thousands of applications. For production systems with high application volumes,
        consider implementing pagination or aggregation pipelines.

    Args:
        job_id: Job ID
        except_application_id: Application ID to exclude (the accepted one)

    Returns:
        Number of applications auto-rejected (0 if except_application_id is invalid)
    """
    collection = get_applications_collection()

    # Validate except_application_id early
    try:
        except_object_id = ObjectId(except_application_id)
    except InvalidId:
        return 0

    try:
        # Update all other applications for this job that aren't already in a final state
        result = await collection.update_many(
            {
                "job_id": job_id,
                "_id": {"$ne": except_object_id},
                "status": {
                    "$nin": [ApplicationStatus.REJECTED.value, ApplicationStatus.ACCEPTED.value]
                },
            },
            {
                "$set": {
                    "status": ApplicationStatus.REJECTED.value,
                    "rejection_reason": "Position filled",
                    "updated_at": datetime.now(UTC),
                    "next_step": "Position has been filled",
                },
                "$push": {
                    "status_history": {
                        "status": ApplicationStatus.REJECTED.value,
                        "changed_at": datetime.now(UTC),
                        "notes": "Position filled - automatically rejected",
                        "changed_by": "system",
                    }
                },
            },
        )

    except Exception:
        return 0
    else:
        return result.modified_count
