from datetime import datetime

from bson import ObjectId

from app.database import get_applications_collection



async def create_application(application_data: dict, job_seeker_id: str) -> dict:
    """
    Create a new job application.

    Args:
        application_data: Application data dictionary
        job_seeker_id: ID of the job seeker applying

    Returns:
        Created application document
    """
    collection = get_applications_collection()

    now = datetime.utcnow()

    # Create status history entry
    initial_status = "Application Submitted"
    status_history_entry = {
        "status": initial_status,
        "changed_at": now,
        "notes": "Application submitted",
        "changed_by": job_seeker_id
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

    return application_doc


async def get_application_by_id(application_id: str) -> dict | None:
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

    return await collection.find_one({"_id": object_id})


async def get_applications(
    skip: int = 0,
    limit: int = 100,
    job_seeker_id: str | None = None,
    job_id: str | None = None,
    status: str | None = None
) -> list[dict]:
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

    query = {}
    if job_seeker_id:
        query["job_seeker_id"] = job_seeker_id
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status

    cursor = collection.find(query).skip(skip).limit(limit).sort("applied_date", -1)
    applications = await cursor.to_list(length=limit)

    return applications


async def update_application(
    application_id: str,
    update_data: dict,
    changed_by: str | None = None
) -> dict | None:
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

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if not update_data:
        return current_app

    update_data["updated_at"] = datetime.utcnow()

    # If status is being changed, add to status history
    if "status" in update_data and update_data["status"] != current_app.get("status"):
        new_status_entry = {
            "status": update_data["status"],
            "changed_at": datetime.utcnow(),
            "notes": update_data.get("notes", "Status changed"),
            "changed_by": changed_by or "system"
        }

        # Add to status history
        result = await collection.find_one_and_update(
            {"_id": object_id},
            {
                "$set": update_data,
                "$push": {"status_history": new_status_entry}
            },
            return_document=True
        )
    else:
        result = await collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=True
        )

    return result


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
    return result.deleted_count > 0


async def get_applications_count(
    job_seeker_id: str | None = None,
    job_id: str | None = None,
    status: str | None = None
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

    query = {}
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

    existing = await collection.find_one({
        "job_seeker_id": job_seeker_id,
        "job_id": job_id
    })

    return existing is not None

