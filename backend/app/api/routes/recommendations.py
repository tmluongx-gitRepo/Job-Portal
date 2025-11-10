"""
API routes for recommendations.
"""

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user, require_admin
from app.crud import job as job_crud
from app.crud import job_seeker_profile as profile_crud
from app.crud import recommendation as recommendation_crud
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationUpdate,
)

router = APIRouter()


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation: RecommendationCreate, _admin: dict = Depends(require_admin)
) -> RecommendationResponse:
    """
    Create a new job recommendation.

    **Requires:** Admin account (service-only operation)

    - **job_seeker_id**: ID of the job seeker
    - **job_id**: ID of the job being recommended
    - **match_percentage**: Match score (0-100)
    - **reasoning**: Why this job is recommended
    - **factors**: Breakdown of matching factors

    This endpoint is typically called by an AI/ML recommendation engine.
    """
    # Verify job seeker exists
    profile = await profile_crud.get_profile_by_id(recommendation.job_seeker_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job seeker profile {recommendation.job_seeker_id} not found",
        )

    # Verify job exists
    job = await job_crud.get_job_by_id(recommendation.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {recommendation.job_id} not found"
        )

    # Check if recommendation already exists
    exists = await recommendation_crud.check_recommendation_exists(
        recommendation.job_seeker_id, recommendation.job_id
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recommendation already exists for this job seeker and job",
        )

    # Create recommendation
    recommendation_data = recommendation.model_dump()
    created_recommendation = await recommendation_crud.create_recommendation(recommendation_data)

    return RecommendationResponse(
        id=str(created_recommendation["_id"]),
        **cast(Any, {k: v for k, v in created_recommendation.items() if k != "_id"}),
    )


@router.get("/job-seeker/{job_seeker_id}", response_model=list[dict])
async def get_recommendations_for_job_seeker(
    job_seeker_id: str,
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_match: int = Query(0, ge=0, le=100, description="Minimum match percentage"),
    include_viewed: bool = Query(True, description="Include viewed recommendations"),
    include_dismissed: bool = Query(False, description="Include dismissed recommendations"),
    include_applied: bool = Query(False, description="Include applied recommendations"),
) -> list[dict]:
    """
    Get personalized job recommendations for a job seeker.

    **Requires:** Authentication
    **Authorization:** Can only view your own recommendations (admins can view all)

    - **job_seeker_id**: Job seeker profile ID
    - **min_match**: Minimum match percentage filter
    - **include_viewed**: Show recommendations user has already viewed
    - **include_dismissed**: Show recommendations user dismissed
    - **include_applied**: Show jobs user already applied to

    Returns recommendations sorted by match percentage (highest first) with full job details.
    """
    # Verify user can access these recommendations
    from app.auth.utils import is_admin

    if not is_admin(current_user):
        # Get user's job seeker profile
        profile = await profile_crud.get_profile_by_user_id(current_user["id"])
        if not profile or str(profile["_id"]) != job_seeker_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own recommendations",
            )

    recommendations = await recommendation_crud.get_recommendations_for_job_seeker(
        job_seeker_id=job_seeker_id,
        skip=skip,
        limit=limit,
        min_match_percentage=min_match,
        include_viewed=include_viewed,
        include_dismissed=include_dismissed,
        include_applied=include_applied,
    )

    # Format response with job details
    response = []
    for rec in recommendations:
        job_details = rec.pop("job_details", {})
        response.append(
            {
                "id": str(rec["_id"]),
                "job_seeker_id": rec["job_seeker_id"],
                "job_id": rec["job_id"],
                "match_percentage": rec["match_percentage"],
                "reasoning": rec["reasoning"],
                "factors": rec["factors"],
                "ai_generated": rec.get("ai_generated", True),
                "viewed": rec.get("viewed", False),
                "dismissed": rec.get("dismissed", False),
                "applied": rec.get("applied", False),
                "created_at": rec["created_at"],
                "job_title": job_details.get("title"),
                "job_company": job_details.get("company"),
                "job_location": job_details.get("location"),
                "job_salary_min": job_details.get("salary_min"),
                "job_salary_max": job_details.get("salary_max"),
                "job_type": job_details.get("job_type"),
            }
        )

    return response


@router.get("/job/{job_id}/candidates", response_model=list[dict])
async def get_matching_candidates_for_job(
    job_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_match: int = Query(70, ge=0, le=100, description="Minimum match percentage"),
) -> list[dict]:
    """
    Get recommended candidates for a specific job (for employers).

    - **job_id**: Job ID
    - **min_match**: Minimum match percentage

    Returns top matching candidates sorted by match percentage.
    """
    recommendations = await recommendation_crud.get_recommendations_for_job(
        job_id=job_id, skip=skip, limit=limit, min_match_percentage=min_match
    )

    # Format response
    response = []
    for rec in recommendations:
        seeker_details = rec.pop("seeker_details", {})
        response.append(
            {
                "id": str(rec["_id"]),
                "job_seeker_id": rec["job_seeker_id"],
                "match_percentage": rec["match_percentage"],
                "reasoning": rec["reasoning"],
                "factors": rec["factors"],
                "seeker_name": seeker_details.get("name"),
                "seeker_skills": seeker_details.get("skills", []),
                "seeker_experience_years": seeker_details.get("experience_years"),
                "seeker_location": seeker_details.get("location"),
                "created_at": rec["created_at"],
            }
        )

    return response


@router.get("/count/{job_seeker_id}")
async def count_recommendations(
    job_seeker_id: str,
    viewed: bool | None = Query(None, description="Filter by viewed status"),
    dismissed: bool | None = Query(None, description="Filter by dismissed status"),
) -> dict[str, int]:
    """
    Get count of recommendations for a job seeker.

    Useful for showing notification badges like "3 new recommendations!"
    """
    count = await recommendation_crud.get_recommendations_count(
        job_seeker_id=job_seeker_id, viewed=viewed, dismissed=dismissed
    )
    return {"count": count}


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: str, current_user: dict = Depends(get_current_user)
) -> RecommendationResponse:
    """
    Get a specific recommendation by ID.

    **Requires:** Authentication
    **Authorization:** Owner only (admins can view all)
    """
    recommendation = await recommendation_crud.get_recommendation_by_id(recommendation_id)

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    # Verify ownership
    from app.auth.utils import is_admin

    if not is_admin(current_user):
        profile = await profile_crud.get_profile_by_user_id(current_user["id"])
        if not profile or str(recommendation.get("job_seeker_id")) != str(profile["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own recommendations",
            )

    return RecommendationResponse(
        id=str(recommendation["_id"]),
        **cast(Any, {k: v for k, v in recommendation.items() if k != "_id"}),
    )


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: str, recommendation_update: RecommendationUpdate
) -> RecommendationResponse:
    """
    Update a recommendation (mark as viewed, dismissed, or applied).

    - **viewed**: User viewed this recommendation
    - **dismissed**: User is not interested
    - **applied**: User applied to this job
    """
    # Check if recommendation exists
    existing = await recommendation_crud.get_recommendation_by_id(recommendation_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    # Update
    update_data = recommendation_update.model_dump(exclude_unset=True)
    updated = await recommendation_crud.update_recommendation(recommendation_id, update_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    return RecommendationResponse(
        id=str(updated["_id"]), **cast(Any, {k: v for k, v in updated.items() if k != "_id"})
    )


@router.post("/{recommendation_id}/view", status_code=status.HTTP_200_OK)
async def mark_recommendation_viewed(recommendation_id: str) -> dict[str, str]:
    """
    Mark a recommendation as viewed.

    Quick endpoint for tracking when user views a recommendation.
    """
    success = await recommendation_crud.mark_as_viewed(recommendation_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    return {"message": "Marked as viewed"}


@router.post("/{recommendation_id}/dismiss", status_code=status.HTTP_200_OK)
async def dismiss_recommendation(recommendation_id: str) -> dict[str, str]:
    """
    Dismiss a recommendation (user not interested).
    """
    success = await recommendation_crud.mark_as_dismissed(recommendation_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    return {"message": "Recommendation dismissed"}


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(recommendation_id: str) -> None:
    """
    Delete a recommendation.
    """
    deleted = await recommendation_crud.delete_recommendation(recommendation_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )
