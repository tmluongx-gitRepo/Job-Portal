"""
CRUD operations for recommendations.
"""

from datetime import UTC, datetime

from bson import ObjectId

from app.database import (
    get_job_seeker_profiles_collection,
    get_jobs_collection,
    get_recommendations_collection,
)


async def create_recommendation(recommendation_data: dict) -> dict:
    """
    Create a new recommendation.

    Args:
        recommendation_data: Recommendation data dictionary

    Returns:
        Created recommendation document
    """
    collection = get_recommendations_collection()

    recommendation_doc = {
        **recommendation_data,
        "viewed": False,
        "dismissed": False,
        "applied": False,
        "created_at": datetime.now(UTC),
    }

    result = await collection.insert_one(recommendation_doc)
    recommendation_doc["_id"] = result.inserted_id

    return recommendation_doc


async def get_recommendation_by_id(recommendation_id: str) -> dict | None:
    """
    Get a recommendation by ID.

    Args:
        recommendation_id: Recommendation ID

    Returns:
        Recommendation document or None
    """
    collection = get_recommendations_collection()

    try:
        object_id = ObjectId(recommendation_id)
    except Exception:
        return None

    return await collection.find_one({"_id": object_id})


async def get_recommendations_for_job_seeker(
    job_seeker_id: str,
    skip: int = 0,
    limit: int = 20,
    min_match_percentage: int = 0,
    include_viewed: bool = True,
    include_dismissed: bool = False,
    include_applied: bool = False,
) -> list[dict]:
    """
    Get recommendations for a job seeker with enriched details.

    Args:
        job_seeker_id: Job seeker ID
        skip: Number to skip
        limit: Maximum to return
        min_match_percentage: Minimum match percentage filter
        include_viewed: Include viewed recommendations
        include_dismissed: Include dismissed recommendations
        include_applied: Include applied recommendations

    Returns:
        List of recommendation documents with job details
    """
    recommendations_collection = get_recommendations_collection()
    jobs_collection = get_jobs_collection()

    # Build query
    query = {"job_seeker_id": job_seeker_id, "match_percentage": {"$gte": min_match_percentage}}

    if not include_viewed:
        query["viewed"] = False
    if not include_dismissed:
        query["dismissed"] = False
    if not include_applied:
        query["applied"] = False

    # Get recommendations sorted by match percentage
    cursor = (
        recommendations_collection.find(query).skip(skip).limit(limit).sort("match_percentage", -1)
    )
    recommendations = await cursor.to_list(length=limit)

    # Enrich with job details
    enriched_recommendations = []
    for rec in recommendations:
        job_id = rec.get("job_id")

        try:
            job_object_id = ObjectId(job_id)
            job = await jobs_collection.find_one({"_id": job_object_id})

            # Skip if job doesn't exist or is inactive
            if not job or not job.get("is_active", True):
                continue

            rec["job_details"] = {
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "job_type": job.get("job_type"),
            }

            enriched_recommendations.append(rec)
        except Exception:
            continue

    return enriched_recommendations


async def get_recommendations_for_job(
    job_id: str, skip: int = 0, limit: int = 20, min_match_percentage: int = 70
) -> list[dict]:
    """
    Get top candidate recommendations for a job.

    Args:
        job_id: Job ID
        skip: Number to skip
        limit: Maximum to return
        min_match_percentage: Minimum match percentage

    Returns:
        List of recommendations with job seeker details
    """
    recommendations_collection = get_recommendations_collection()

    query = {"job_id": job_id, "match_percentage": {"$gte": min_match_percentage}}

    cursor = (
        recommendations_collection.find(query).skip(skip).limit(limit).sort("match_percentage", -1)
    )
    recommendations = await cursor.to_list(length=limit)

    # Enrich with job seeker details
    enriched_recommendations = []
    for rec in recommendations:
        seeker_id = rec.get("job_seeker_id")

        try:
            seeker_object_id = ObjectId(seeker_id)
            profiles_collection = get_job_seeker_profiles_collection()
            profile = await profiles_collection.find_one({"_id": seeker_object_id})

            if profile:
                rec["seeker_details"] = {
                    "name": f"{profile.get('first_name', '')} {profile.get('last_name', '')}",
                    "skills": profile.get("skills", []),
                    "experience_years": profile.get("experience_years"),
                    "location": profile.get("location"),
                }
                enriched_recommendations.append(rec)
        except Exception:
            continue

    return enriched_recommendations


async def update_recommendation(recommendation_id: str, update_data: dict) -> dict | None:
    """
    Update a recommendation.

    Args:
        recommendation_id: Recommendation ID
        update_data: Fields to update

    Returns:
        Updated recommendation or None
    """
    collection = get_recommendations_collection()

    try:
        object_id = ObjectId(recommendation_id)
    except Exception:
        return None

    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    if not update_data:
        return await get_recommendation_by_id(recommendation_id)

    return await collection.find_one_and_update(
        {"_id": object_id}, {"$set": update_data}, return_document=True
    )


async def mark_as_viewed(recommendation_id: str) -> bool:
    """
    Mark a recommendation as viewed.

    Args:
        recommendation_id: Recommendation ID

    Returns:
        True if successful
    """
    result = await update_recommendation(recommendation_id, {"viewed": True})
    return result is not None


async def mark_as_dismissed(recommendation_id: str) -> bool:
    """
    Mark a recommendation as dismissed.

    Args:
        recommendation_id: Recommendation ID

    Returns:
        True if successful
    """
    result = await update_recommendation(recommendation_id, {"dismissed": True})
    return result is not None


async def mark_as_applied(recommendation_id: str) -> bool:
    """
    Mark a recommendation as applied.

    Args:
        recommendation_id: Recommendation ID

    Returns:
        True if successful
    """
    result = await update_recommendation(recommendation_id, {"applied": True})
    return result is not None


async def delete_recommendation(recommendation_id: str) -> bool:
    """
    Delete a recommendation.

    Args:
        recommendation_id: Recommendation ID

    Returns:
        True if deleted
    """
    collection = get_recommendations_collection()

    try:
        object_id = ObjectId(recommendation_id)
    except Exception:
        return False

    result = await collection.delete_one({"_id": object_id})
    return result.deleted_count > 0


async def get_recommendations_count(
    job_seeker_id: str, viewed: bool | None = None, dismissed: bool | None = None
) -> int:
    """
    Get count of recommendations for a job seeker.

    Args:
        job_seeker_id: Job seeker ID
        viewed: Filter by viewed status
        dismissed: Filter by dismissed status

    Returns:
        Count of recommendations
    """
    collection = get_recommendations_collection()

    query = {"job_seeker_id": job_seeker_id}
    if viewed is not None:
        query["viewed"] = viewed
    if dismissed is not None:
        query["dismissed"] = dismissed

    return await collection.count_documents(query)


async def check_recommendation_exists(job_seeker_id: str, job_id: str) -> bool:
    """
    Check if a recommendation already exists.

    Args:
        job_seeker_id: Job seeker ID
        job_id: Job ID

    Returns:
        True if exists
    """
    collection = get_recommendations_collection()

    count = await collection.count_documents({"job_seeker_id": job_seeker_id, "job_id": job_id})

    return count > 0
