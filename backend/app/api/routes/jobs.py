from collections.abc import Iterable

from fastapi import APIRouter, HTTPException, Query, status

from app.crud import job as job_crud
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.types import JobDocument

router = APIRouter()


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
    return [_serialize_job(doc) for doc in documents]


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    posted_by: str | None = Query(None, description="User ID of employer posting the job"),
)-> JobResponse:
    """
    Create a new job posting.

    - **posted_by**: Optional user ID of the employer who posted this job
    """
    job_data = job.model_dump()

    created_job = await job_crud.create_job(job_data, posted_by=posted_by)

    return _serialize_job(created_job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
)-> list[JobResponse]:
    """
    List all jobs with optional filters.

    - **skip**: Number of jobs to skip (for pagination)
    - **limit**: Maximum number of jobs to return
    - **is_active**: Filter by active/inactive status
    - **posted_by**: Filter by employer user ID
    """
    jobs = await job_crud.get_jobs(skip=skip, limit=limit, is_active=is_active, posted_by=posted_by)

    return _serialize_jobs(jobs)


@router.get("/count")
async def count_jobs(
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
)-> dict[str, int]:
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
)-> list[JobResponse]:
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
)-> JobResponse:
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
async def update_job(job_id: str, job_update: JobUpdate) -> JobResponse:
    """
    Update a job.

    - **job_id**: Job ID
    - Provide only the fields you want to update
    """
    # Check if job exists
    existing_job = await job_crud.get_job_by_id(job_id)
    if not existing_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    # Update the job
    update_data = job_update.model_dump(exclude_unset=True)
    updated_job = await job_crud.update_job(job_id, update_data)

    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )

    return _serialize_job(updated_job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str) -> None:
    """
    Delete a job (hard delete).

    - **job_id**: Job ID
    """
    deleted = await job_crud.delete_job(job_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )
