"""API routes for recommendations."""

from collections.abc import Iterable

from fastapi import APIRouter, HTTPException, Query, status

from app.crud import job as job_crud
from app.crud import job_seeker_profile as profile_crud
from app.crud import recommendation as recommendation_crud
from app.schemas.recommendation import (
    MatchFactorSchema,
    RecommendationCreate,
    RecommendationResponse,
    RecommendationUpdate,
)
from app.types import MatchFactorDocument, RecommendationDocument

router = APIRouter()


def _convert_factors(raw_factors: Iterable[MatchFactorDocument] | None) -> list[MatchFactorSchema]:
    """Convert stored factor dictionaries into schema objects."""

    if not raw_factors:
        return []
    return [MatchFactorSchema.model_validate(factor) for factor in raw_factors]


def _serialize_recommendation(document: RecommendationDocument) -> RecommendationResponse:
    """Convert a database document into the API response schema."""

    return RecommendationResponse(
        id=str(document["_id"]),
        job_seeker_id=document["job_seeker_id"],
        job_id=document["job_id"],
        match_percentage=document["match_percentage"],
        reasoning=document["reasoning"],
        factors=_convert_factors(document.get("factors")),
        ai_generated=document.get("ai_generated", True),
        viewed=document.get("viewed", False),
        dismissed=document.get("dismissed", False),
        applied=document.get("applied", False),
        created_at=document["created_at"],
    )


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(recommendation: RecommendationCreate) -> RecommendationResponse:
    """
    Create a new job recommendation.

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

    return _serialize_recommendation(created_recommendation)


@router.get("/job-seeker/{job_seeker_id}", response_model=list[dict])
async def get_recommendations_for_job_seeker(
    job_seeker_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_match: int = Query(0, ge=0, le=100, description="Minimum match percentage"),
    include_viewed: bool = Query(True, description="Include viewed recommendations"),
    include_dismissed: bool = Query(False, description="Include dismissed recommendations"),
    include_applied: bool = Query(False, description="Include applied recommendations"),
)-> list[dict[str, object]]:
    """
    Get personalized job recommendations for a job seeker.

    - **job_seeker_id**: Job seeker ID
    - **min_match**: Minimum match percentage filter
    - **include_viewed**: Show recommendations user has already viewed
    - **include_dismissed**: Show recommendations user dismissed
    - **include_applied**: Show jobs user already applied to

    Returns recommendations sorted by match percentage (highest first) with full job details.
    """
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
        job_details = rec.get("job_details", {})
        response.append(
            {
                "id": str(rec["_id"]),
                "job_seeker_id": rec["job_seeker_id"],
                "job_id": rec["job_id"],
                "match_percentage": rec["match_percentage"],
                "reasoning": rec["reasoning"],
                "factors": rec.get("factors", []),
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
)-> list[dict[str, object]]:
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
        seeker_details = rec.get("seeker_details", {})
        response.append(
            {
                "id": str(rec["_id"]),
                "job_seeker_id": rec["job_seeker_id"],
                "match_percentage": rec["match_percentage"],
                "reasoning": rec["reasoning"],
                "factors": rec.get("factors", []),
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
)-> dict[str, int]:
    """
    Get count of recommendations for a job seeker.

    Useful for showing notification badges like "3 new recommendations!"
    """
    count = await recommendation_crud.get_recommendations_count(
        job_seeker_id=job_seeker_id, viewed=viewed, dismissed=dismissed
    )
    return {"count": count}


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(recommendation_id: str) -> RecommendationResponse:
    """
    Get a specific recommendation by ID.
    """
    recommendation = await recommendation_crud.get_recommendation_by_id(recommendation_id)

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found",
        )

    return _serialize_recommendation(recommendation)


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

    return _serialize_recommendation(updated)


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
