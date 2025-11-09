from fastapi import APIRouter, HTTPException, Query, status


from app.crud import application as application_crud
from app.crud import job as job_crud
from app.crud import job_seeker_profile as profile_crud
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(application: ApplicationCreate):
    """
    Create a new job application.

    - **job_seeker_id**: ID of the job seeker profile applying
    - **job_id**: ID of the job being applied to
    - **notes**: Optional notes from the applicant

    This will:
    - Check if the job seeker has already applied to this job
    - Verify that the job and job seeker profile exist
    - Increment the job's application count
    """
    # Check if job seeker profile exists
    profile = await profile_crud.get_profile_by_id(application.job_seeker_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job seeker profile with id {application.job_seeker_id} not found"
        )

    # Check if job exists
    job = await job_crud.get_job_by_id(application.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {application.job_id} not found"
        )

    # Check if job is active
    if not job.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to an inactive job"
        )

    # Check for duplicate application
    is_duplicate = await application_crud.check_duplicate_application(
        application.job_seeker_id,
        application.job_id
    )
    if is_duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job"
        )

    # Create the application
    application_data = application.model_dump()
    created_application = await application_crud.create_application(
        application_data,
        job_seeker_id=application.job_seeker_id
    )

    # Increment the job's application count
    await job_crud.increment_application_count(application.job_id)

    return ApplicationResponse(
        id=str(created_application["_id"]),
        **{k: v for k, v in created_application.items() if k != "_id"}
    )


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of applications to return"),
    job_seeker_id: str | None = Query(None, description="Filter by job seeker ID"),
    job_id: str | None = Query(None, description="Filter by job ID"),
    status: str | None = Query(None, description="Filter by status")
):
    """
    List all applications with optional filters.

    - **skip**: Number of applications to skip (for pagination)
    - **limit**: Maximum number of applications to return
    - **job_seeker_id**: Filter by job seeker profile ID
    - **job_id**: Filter by job ID
    - **status**: Filter by application status
    """
    applications = await application_crud.get_applications(
        skip=skip,
        limit=limit,
        job_seeker_id=job_seeker_id,
        job_id=job_id,
        status=status
    )

    return [
        ApplicationResponse(
            id=str(app["_id"]),
            **{k: v for k, v in app.items() if k != "_id"}
        )
        for app in applications
    ]


@router.get("/count")
async def count_applications(
    job_seeker_id: str | None = Query(None, description="Filter by job seeker ID"),
    job_id: str | None = Query(None, description="Filter by job ID"),
    status: str | None = Query(None, description="Filter by status")
):
    """
    Get the total count of applications.

    - **job_seeker_id**: Filter by job seeker profile ID
    - **job_id**: Filter by job ID
    - **status**: Filter by application status
    """
    count = await application_crud.get_applications_count(
        job_seeker_id=job_seeker_id,
        job_id=job_id,
        status=status
    )
    return {"count": count}


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str):
    """
    Get a specific application by ID.

    - **application_id**: Application ID
    """
    application = await application_crud.get_application_by_id(application_id)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    return ApplicationResponse(
        id=str(application["_id"]),
        **{k: v for k, v in application.items() if k != "_id"}
    )


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    changed_by: str | None = Query(None, description="User ID making the change")
):
    """
    Update an application.

    - **application_id**: Application ID
    - **changed_by**: Optional user ID for tracking who made the change
    - Provide only the fields you want to update

    If the status is changed, it will be recorded in the status history.
    """
    # Check if application exists
    existing_application = await application_crud.get_application_by_id(application_id)
    if not existing_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    # Update the application
    update_data = application_update.model_dump(exclude_unset=True)
    updated_application = await application_crud.update_application(
        application_id,
        update_data,
        changed_by=changed_by
    )

    if not updated_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    return ApplicationResponse(
        id=str(updated_application["_id"]),
        **{k: v for k, v in updated_application.items() if k != "_id"}
    )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: str):
    """
    Delete an application (hard delete).

    - **application_id**: Application ID
    """
    deleted = await application_crud.delete_application(application_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )


