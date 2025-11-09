from datetime import datetime

from bson import ObjectId

from app.database import get_jobs_collection



async def create_job(job_data: dict, posted_by: str | None = None) -> dict:
    """
    Create a new job posting.

    Args:
        job_data: Job data dictionary
        posted_by: User ID of the employer who posted the job

    Returns:
        Created job document
    """
    collection = get_jobs_collection()

    job_doc = {
        **job_data,
        "posted_by": posted_by,
        "is_active": True,
        "view_count": 0,
        "application_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await collection.insert_one(job_doc)
    job_doc["_id"] = result.inserted_id

    return job_doc


async def get_job_by_id(job_id: str, increment_views: bool = False) -> dict | None:
    """
    Get a job by ID.

    Args:
        job_id: Job ID
        increment_views: Whether to increment the view count

    Returns:
        Job document or None if not found
    """
    collection = get_jobs_collection()

    try:
        object_id = ObjectId(job_id)
    except Exception:
        return None

    if increment_views:
        # Increment view count and return updated document
        job = await collection.find_one_and_update(
            {"_id": object_id},
            {"$inc": {"view_count": 1}},
            return_document=True
        )
    else:
        job = await collection.find_one({"_id": object_id})

    return job


async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    posted_by: str | None = None
) -> list[dict]:
    """
    Get a list of jobs with optional filters.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        is_active: Filter by active status
        posted_by: Filter by employer user ID

    Returns:
        List of job documents
    """
    collection = get_jobs_collection()

    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    if posted_by:
        query["posted_by"] = posted_by

    cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
    jobs = await cursor.to_list(length=limit)

    return jobs


async def search_jobs(
    query: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    remote_ok: bool | None = None,
    skills: list[str | None] = None,
    min_salary: int | None = None,
    max_salary: int | None = None,
    experience_required: str | None = None,
    industry: str | None = None,
    company_size: str | None = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100
) -> list[dict]:
    """
    Search for jobs with multiple filters.

    Args:
        query: Text search in title, description, company
        location: Location filter
        job_type: Job type filter
        remote_ok: Remote work filter
        skills: Skills filter (any of the skills)
        min_salary: Minimum salary filter
        max_salary: Maximum salary filter
        experience_required: Experience level filter
        industry: Industry filter
        company_size: Company size filter
        is_active: Filter by active status
        skip: Number of documents to skip
        limit: Maximum number of documents to return

    Returns:
        List of job documents
    """
    collection = get_jobs_collection()

    filters = {"is_active": is_active}

    # Text search in title, description, company
    if query:
        filters["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"company": {"$regex": query, "$options": "i"}},
        ]

    # Location filter
    if location:
        filters["location"] = {"$regex": location, "$options": "i"}

    # Job type filter
    if job_type:
        filters["job_type"] = job_type

    # Remote filter
    if remote_ok is not None:
        filters["remote_ok"] = remote_ok

    # Skills filter - any of the provided skills
    if skills and len(skills) > 0:
        filters["skills_required"] = {"$in": skills}

    # Salary filters
    if min_salary is not None:
        filters["salary_max"] = {"$gte": min_salary}
    if max_salary is not None:
        filters["salary_min"] = {"$lte": max_salary}

    # Experience filter
    if experience_required:
        filters["experience_required"] = experience_required

    # Industry filter
    if industry:
        filters["industry"] = {"$regex": industry, "$options": "i"}

    # Company size filter
    if company_size:
        filters["company_size"] = company_size

    cursor = collection.find(filters).skip(skip).limit(limit).sort("created_at", -1)
    jobs = await cursor.to_list(length=limit)

    return jobs


async def update_job(job_id: str, update_data: dict) -> dict | None:
    """
    Update a job.

    Args:
        job_id: Job ID
        update_data: Fields to update

    Returns:
        Updated job document or None if not found
    """
    collection = get_jobs_collection()

    try:
        object_id = ObjectId(job_id)
    except Exception:
        return None

    # Remove None values and add updated_at
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if not update_data:
        return await get_job_by_id(job_id)

    update_data["updated_at"] = datetime.utcnow()

    result = await collection.find_one_and_update(
        {"_id": object_id},
        {"$set": update_data},
        return_document=True
    )

    return result


async def increment_application_count(job_id: str) -> bool:
    """
    Increment the application count for a job.

    Args:
        job_id: Job ID

    Returns:
        True if successful, False otherwise
    """
    collection = get_jobs_collection()

    try:
        object_id = ObjectId(job_id)
    except Exception:
        return False

    result = await collection.update_one(
        {"_id": object_id},
        {"$inc": {"application_count": 1}}
    )

    return result.modified_count > 0


async def delete_job(job_id: str) -> bool:
    """
    Delete a job (hard delete).

    Args:
        job_id: Job ID

    Returns:
        True if deleted, False if not found
    """
    collection = get_jobs_collection()

    try:
        object_id = ObjectId(job_id)
    except Exception:
        return False

    result = await collection.delete_one({"_id": object_id})
    return result.deleted_count > 0


async def get_jobs_count(is_active: bool | None = None, posted_by: str | None = None) -> int:
    """
    Get the total count of jobs.

    Args:
        is_active: Filter by active status
        posted_by: Filter by employer user ID

    Returns:
        Total count of jobs
    """
    collection = get_jobs_collection()

    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    if posted_by:
        query["posted_by"] = posted_by

    return await collection.count_documents(query)

