from fastapi import APIRouter, HTTPException, Query, status

from app.crud import job as job_crud
from app.schemas.job import JobCreate, JobResponse, JobUpdate

router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    posted_by: str | None = Query(None, description="User ID of employer posting the job"),
):
    """
    Create a new job posting.

    - **posted_by**: Optional user ID of the employer who posted this job
    """
    job_data = job.model_dump()

    created_job = await job_crud.create_job(job_data, posted_by=posted_by)

    return JobResponse(
        id=str(created_job["_id"]), **{k: v for k, v in created_job.items() if k != "_id"}
    )


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
):
    """
    List all jobs with optional filters.

    - **skip**: Number of jobs to skip (for pagination)
    - **limit**: Maximum number of jobs to return
    - **is_active**: Filter by active/inactive status
    - **posted_by**: Filter by employer user ID
    """
    jobs = await job_crud.get_jobs(skip=skip, limit=limit, is_active=is_active, posted_by=posted_by)

    return [
        JobResponse(id=str(job["_id"]), **{k: v for k, v in job.items() if k != "_id"})
        for job in jobs
    ]


@router.get("/count")
async def count_jobs(
    is_active: bool | None = Query(None, description="Filter by active status"),
    posted_by: str | None = Query(None, description="Filter by employer user ID"),
):
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
    skills: list[str | None] = Query(None, description="Skills filter (any of these skills)"),
    min_salary: int | None = Query(None, ge=0, description="Minimum salary"),
    max_salary: int | None = Query(None, ge=0, description="Maximum salary"),
    experience_required: str | None = Query(None, description="Experience level required"),
    industry: str | None = Query(None, description="Industry filter"),
    company_size: str | None = Query(None, description="Company size filter"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of jobs to return"),
):
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

    return [
        JobResponse(id=str(job["_id"]), **{k: v for k, v in job.items() if k != "_id"})
        for job in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str, increment_views: bool = Query(False, description="Whether to increment view count")
):
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

    return JobResponse(id=str(job["_id"]), **{k: v for k, v in job.items() if k != "_id"})


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job_update: JobUpdate):
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

    return JobResponse(
        id=str(updated_job["_id"]), **{k: v for k, v in updated_job.items() if k != "_id"}
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str):
    """
    Delete a job (hard delete).

    - **job_id**: Job ID
    """
    deleted = await job_crud.delete_job(job_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with id {job_id} not found"
        )
