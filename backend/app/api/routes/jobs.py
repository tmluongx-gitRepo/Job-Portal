import asyncio
import logging
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_utils import is_admin
from app.auth.dependencies import get_current_user, get_optional_user, require_employer
from app.constants import InterviewStatus
from app.crud import employer_profile as profile_crud
from app.crud import job as job_crud
from app.database import get_applications_collection, get_interviews_collection
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.stats import JobAnalyticsResponse
from app.tasks.embedding_tasks import process_jobs, remove_jobs
from app.type_definitions import JobDocument
from app.utils.datetime_utils import ensure_utc_datetime

router = APIRouter()
logger = logging.getLogger(__name__)


def _serialize_job(document: JobDocument) -> JobResponse:
    """Convert a job document into the API response schema."""
    responsibilities = document.get("responsibilities", [])
    skills_required = document.get("skills_required", [])
    benefits = document.get("benefits", [])

    return JobResponse(
        id=str(document["_id"]),
        title=document["title"],
        company=document["company"],
        description=document["description"],
        requirements=document.get("requirements"),
        responsibilities=responsibilities,
        location=document["location"],
        job_type=document.get("job_type", ""),
        remote_ok=document.get("remote_ok", False),
        salary_min=document.get("salary_min"),
        salary_max=document.get("salary_max"),
        experience_required=document.get("experience_required"),
        education_required=document.get("education_required"),
        industry=document.get("industry"),
        company_size=document.get("company_size"),
        benefits=benefits,
        skills_required=skills_required,
        application_deadline=document.get("application_deadline"),
        is_active=document.get("is_active", True),
        view_count=document.get("view_count", 0),
        application_count=document.get("application_count", 0),
        posted_by=document.get("posted_by"),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _serialize_jobs(documents: Iterable[JobDocument]) -> list[JobResponse]:
    """Convert multiple job documents into API response schemas."""
    return [_serialize_job(doc) for doc in documents]


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, employer: dict = Depends(require_employer)) -> JobResponse:
    """
    Create a new job posting.

    **Requires:** Employer account with profile

    The job will be automatically linked to the authenticated employer.
    Employers must have a profile before posting jobs.
    """
    # Check if employer has a profile
    employer_profile = await profile_crud.get_profile_by_user_id(employer["id"])
    if not employer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must create an employer profile before posting jobs",
        )

    job_data = job.model_dump()

    # Use authenticated user's ID as posted_by
    created_job = await job_crud.create_job(job_data, posted_by=employer["id"])

    _schedule_job_embedding(str(created_job["_id"]))

    return _serialize_job(created_job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
    current_user: dict | None = Depends(get_optional_user),
) -> list[JobResponse]:
    """
    List all jobs with optional filters.

    **Public endpoint** - No authentication required.

    - **skip**: Number of jobs to skip (for pagination)
    - **limit**: Maximum number of jobs to return
    - **is_active**: Filter by active/inactive status
    - **posted_by**: Filter by employer user ID

    If authenticated, you can see all your posted jobs (including inactive).
    If not authenticated, you only see active jobs.
    """
    # If user is authenticated and filtering their own jobs, show all statuses
    if current_user and posted_by == current_user["id"]:
        jobs = await job_crud.get_jobs(
            skip=skip, limit=limit, is_active=is_active, posted_by=posted_by
        )
    else:
        # For non-owners, only show active jobs
        jobs = await job_crud.get_jobs(skip=skip, limit=limit, is_active=True, posted_by=posted_by)

    return _serialize_jobs(jobs)


@router.get("/count")
async def count_jobs(
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
) -> dict[str, int]:
    """
    Get the total count of jobs.

    - **is_active**: Filter by active/inactive status
    - **posted_by**: Filter by employer user ID
    """
    count = await job_crud.get_jobs_count(is_active=is_active, posted_by=posted_by)
    return {"count": count}


@router.get("/search", response_model=list[JobResponse])
async def search_jobs(
    query: str | None = Query(None, description="Search text (title, description, company)"),
    location: str | None = Query(None, description="Location filter"),
    job_type: str | None = Query(None, description="Job type filter"),
    remote_ok: bool | None = Query(None, description="Remote work filter"),
    skills: list[str] | None = Query(None, description="Skills filter (any of these skills)"),
    min_salary: int | None = Query(None, ge=0, description="Minimum salary"),
    max_salary: int | None = Query(None, ge=0, description="Maximum salary"),
    experience_required: str | None = Query(None, description="Experience level required"),
    industry: str | None = Query(None, description="Industry filter"),
    company_size: str | None = Query(None, description="Company size filter"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return"),
) -> list[JobResponse]:
    """
    Search for jobs with multiple filters.

    - **query**: Text search across title, description, and company name
    - **location**: Filter by location (case-insensitive)
    - **job_type**: Filter by job type (Full-time, Part-time, Contract, Internship)
    - **remote_ok**: Filter by remote work availability
    - **skills**: Filter by required skills (matches any of the provided skills)
    - **min_salary**: Minimum salary filter
    - **max_salary**: Maximum salary filter
    - **experience_required**: Filter by experience level
    - **industry**: Filter by industry
    - **company_size**: Filter by company size
    - **is_active**: Filter by active status (default: True)
    """
    jobs = await job_crud.search_jobs(
        query=query,
        location=location,
        job_type=job_type,
        remote_ok=remote_ok,
        skills=skills,
        min_salary=min_salary,
        max_salary=max_salary,
        experience_required=experience_required,
        industry=industry,
        company_size=company_size,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )

    return _serialize_jobs(jobs)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str, increment_views: bool = Query(False, description="Whether to increment view count")
) -> JobResponse:
    """
    Get a specific job by ID.

    - **job_id**: Job ID
    - **increment_views**: Set to true to increment the view counter
    """
    job = await job_crud.get_job_by_id(job_id, increment_views=increment_views)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    return _serialize_job(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str, job_update: JobUpdate, current_user: dict = Depends(get_current_user)
) -> JobResponse:
    """
    Update a job.

    **Requires:** Authentication
    **Authorization:** Only the employer who posted the job can update it (or admins)

    - **job_id**: Job ID
    - Provide only the fields you want to update
    """
    # Check if job exists
    existing_job = await job_crud.get_job_by_id(job_id)
    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    # Check if user is the owner or admin
    # Normalize posted_by to string for comparison (it's stored as ObjectId in MongoDB)
    if str(existing_job.get("posted_by")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only update jobs you posted"
        )

    # Update the job
    update_data = job_update.model_dump(exclude_unset=True)
    updated_job = await job_crud.update_job(job_id, update_data)

    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    _schedule_job_embedding(job_id)

    return _serialize_job(updated_job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete a job (hard delete).

    **Requires:** Authentication
    **Authorization:** Only the employer who posted the job can delete it (or admins)
    """
    # Get the job to check ownership
    existing_job = await job_crud.get_job_by_id(job_id)
    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    # Check if user is the owner or admin
    # Normalize posted_by to string for comparison (it's stored as ObjectId in MongoDB)
    if str(existing_job.get("posted_by")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete jobs you posted"
        )

    deleted = await job_crud.delete_job(job_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    _schedule_job_removal(job_id)


def _schedule_job_embedding(job_id: str) -> None:
    async def _runner() -> None:
        try:
            await process_jobs([job_id])
        except Exception:  # pragma: no cover - background defensive logging
            logger.exception("jobs.embedding_ingest_failed", extra={"job_id": job_id})

    asyncio.create_task(_runner())  # noqa: RUF006


def _schedule_job_removal(job_id: str) -> None:
    async def _runner() -> None:
        try:
            await remove_jobs([job_id])
        except Exception:  # pragma: no cover - background defensive logging
            logger.exception("jobs.embedding_delete_failed", extra={"job_id": job_id})

    asyncio.create_task(_runner())  # noqa: RUF006


@router.get("/{job_id}/analytics", response_model=JobAnalyticsResponse)
async def get_job_analytics(
    job_id: str, current_user: dict = Depends(get_current_user)
) -> JobAnalyticsResponse:
    """
    Get analytics for a specific job posting.

    **Requires:** Authentication
    **Authorization:** Only the employer who posted the job can view analytics (or admins)

    Returns aggregated statistics including:
    - Total applications and breakdown by status
    - Interview metrics (scheduled, completed, average rating)
    - Recent activity (last 7 days)
    - Last application date

    **Note:** Current implementation loads all applications/interviews into memory.
    For production use with large datasets, consider implementing pagination or
    MongoDB aggregation pipelines.
    """
    # Check if job exists
    existing_job = await job_crud.get_job_by_id(job_id)
    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    # Check if user is the owner or admin
    if str(existing_job.get("posted_by")) != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view analytics for jobs you posted",
        )

    applications_collection = get_applications_collection()
    interviews_collection = get_interviews_collection()

    # Get all applications for this job
    applications_cursor = applications_collection.find({"job_id": job_id})
    applications = await applications_cursor.to_list(length=10000)

    total_applications = len(applications)

    # Calculate applications by status
    applications_by_status: dict[str, int] = {}
    for app in applications:
        status_val = app.get("status", "Unknown")
        applications_by_status[status_val] = applications_by_status.get(status_val, 0) + 1

    # Calculate recent applications (last 7 days)
    seven_days_ago = datetime.now(UTC) - timedelta(days=7)
    recent_applications_count = 0
    for app in applications:
        applied_date = app.get("applied_date")
        if applied_date:
            # Ensure timezone-aware comparison using utility function
            applied_date = ensure_utc_datetime(applied_date)
            if applied_date and applied_date >= seven_days_ago:
                recent_applications_count += 1

    # Get last application date
    last_application_date = None
    if applications:
        last_application_date = max(
            (app.get("applied_date") for app in applications if app.get("applied_date")),
            default=None,
        )

    # Get application IDs for interview lookup
    application_ids = [str(app["_id"]) for app in applications]

    # Get interviews for these applications
    interviews_scheduled = 0
    interviews_completed = 0
    ratings: list[float] = []

    if application_ids:
        interviews_cursor = interviews_collection.find({"application_id": {"$in": application_ids}})
        interviews = await interviews_cursor.to_list(length=10000)

        for interview in interviews:
            interview_status = interview.get("status", "")
            if interview_status in [
                InterviewStatus.SCHEDULED.value,
                InterviewStatus.RESCHEDULED.value,
            ]:
                interviews_scheduled += 1
            elif interview_status == InterviewStatus.COMPLETED.value:
                interviews_completed += 1
                rating = interview.get("rating")
                # Validate rating is numeric before adding
                if rating is not None and isinstance(rating, int | float):
                    ratings.append(float(rating))

    # Calculate average interview rating
    avg_interview_rating = sum(ratings) / len(ratings) if ratings else None

    return JobAnalyticsResponse(
        job_id=job_id,
        job_title=existing_job["title"],
        total_applications=total_applications,
        applications_by_status=applications_by_status,
        recent_applications_count=recent_applications_count,
        interviews_scheduled=interviews_scheduled,
        interviews_completed=interviews_completed,
        avg_interview_rating=avg_interview_rating,
        last_application_date=last_application_date,
    )
