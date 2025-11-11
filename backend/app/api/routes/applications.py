from collections.abc import Iterable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user, require_job_seeker
from app.crud import application as application_crud
from app.crud import job as job_crud
from app.crud import job_seeker_profile as profile_crud
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    StatusHistoryEntrySchema,
)
from app.type_definitions import ApplicationDocument

router = APIRouter()


def _serialize_application(document: ApplicationDocument) -> ApplicationResponse:
    """Convert a database document to the response schema."""
    job_id = document.get("job_id", "")
    job_seeker_id = document.get("job_seeker_id", "")
    status_value = document.get("status", "Application Submitted")
    notes = document.get("notes")
    applied_date = document["applied_date"]
    next_step = document.get("next_step")
    interview_scheduled_date = document.get("interview_scheduled_date")
    rejection_reason = document.get("rejection_reason")
    status_history_data = document.get("status_history", [])
    status_history = [StatusHistoryEntrySchema(**entry) for entry in status_history_data]

    return ApplicationResponse(
        id=str(document["_id"]),
        job_id=job_id,
        job_seeker_id=job_seeker_id,
        status=status_value,
        notes=notes,
        applied_date=applied_date,
        next_step=next_step,
        interview_scheduled_date=interview_scheduled_date,
        rejection_reason=rejection_reason,
        status_history=status_history,
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _serialize_applications(
    documents: Iterable[ApplicationDocument],
) -> list[ApplicationResponse]:
    """Convert multiple application documents into API response schemas."""
    return [_serialize_application(doc) for doc in documents]


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate, job_seeker: dict = Depends(require_job_seeker)
) -> ApplicationResponse:
    """
    Create a new job application.

    **Requires:** Job Seeker account

    - **job_seeker_id**: ID of the job seeker profile applying
    - **job_id**: ID of the job being applied to
    - **notes**: Optional notes from the applicant

    This will:
    - Verify you own the job seeker profile
    - Check if the job seeker has already applied to this job
    - Verify that the job and job seeker profile exist
    - Increment the job's application count
    """
    # Check if job seeker profile exists
    profile = await profile_crud.get_profile_by_id(application.job_seeker_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job seeker profile with id {application.job_seeker_id} not found",
        )

    # Verify the job seeker profile belongs to the authenticated user
    if str(profile.get("user_id")) != job_seeker["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only apply with your own job seeker profile",
        )

    # Check if job exists
    job = await job_crud.get_job_by_id(application.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {application.job_id} not found",
        )

    # Check if job is active
    if not job.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot apply to an inactive job"
        )

    # Check for duplicate application
    is_duplicate = await application_crud.check_duplicate_application(
        application.job_seeker_id, application.job_id
    )
    if is_duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You have already applied to this job"
        )

    # Create the application
    application_data = application.model_dump()
    created_application = await application_crud.create_application(
        application_data, job_seeker_id=application.job_seeker_id
    )

    # Increment the job's application count
    await job_crud.increment_application_count(application.job_id)

    return _serialize_application(created_application)


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of applications to return"),
    job_seeker_id: str | None = Query(None, description="Filter by job seeker ID"),
    job_id: str | None = Query(None, description="Filter by job ID"),
    application_status: str | None = Query(None, alias="status", description="Filter by status"),
) -> list[ApplicationResponse]:
    """
    List applications.

    **Requires:** Authentication
    **Authorization:**
    - Job seekers see their own applications
    - Employers see applications to their jobs
    - Admins see all

    - **skip**: Number of applications to skip (for pagination)
    - **limit**: Maximum number of applications to return
    - **job_seeker_id**: Filter by job seeker profile ID
    - **job_id**: Filter by job ID
    - **status**: Filter by application status
    """
    from app.auth.auth_utils import is_admin, is_employer, is_job_seeker

    # Admins can see all applications with any filter
    if is_admin(current_user):
        applications = await application_crud.get_applications(
            skip=skip,
            limit=limit,
            job_seeker_id=job_seeker_id,
            job_id=job_id,
            status=application_status,
        )
    elif is_job_seeker(current_user):
        # Job seekers can only see their own applications
        # Get their job seeker profile
        profile = await profile_crud.get_profile_by_user_id(current_user["id"])
        if not profile:
            return []  # No profile = no applications

        # Force filter to their profile
        applications = await application_crud.get_applications(
            skip=skip,
            limit=limit,
            job_seeker_id=str(profile["_id"]),
            job_id=job_id,
            status=application_status,
        )
    elif is_employer(current_user):
        # Employers can see applications to their jobs
        # Get jobs posted by this employer
        employer_jobs = await job_crud.get_jobs(posted_by=current_user["id"])
        employer_job_ids = [str(job["_id"]) for job in employer_jobs]

        if not employer_job_ids:
            return []  # No jobs = no applications

        # If filtering by specific job_id, verify they own it
        if job_id and job_id not in employer_job_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view applications to your own jobs",
            )

        # Get applications for their jobs
        if job_id:
            # If filtering by specific job, use it directly (already verified ownership above)
            applications = await application_crud.get_applications(
                skip=skip,
                limit=limit,
                job_seeker_id=job_seeker_id,
                job_id=job_id,
                status=application_status,
            )
        else:
            # Fetch all applications and filter by employer's jobs
            # Note: This fetches more than limit to account for filtering
            # A better solution would be to add multi-job_id support to CRUD
            all_applications = await application_crud.get_applications(
                skip=0,
                limit=1000,  # Fetch more to ensure we have enough after filtering
                job_seeker_id=job_seeker_id,
                job_id=None,
                status=application_status,
            )
            # Filter to only applications for their jobs
            filtered = [
                app for app in all_applications if str(app.get("job_id")) in employer_job_ids
            ]
            # Apply pagination after filtering
            applications = filtered[skip : skip + limit]
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account type")

    return _serialize_applications(applications)


@router.get("/count")
async def count_applications(
    job_seeker_id: str | None = Query(None, description="Filter by job seeker ID"),
    job_id: str | None = Query(None, description="Filter by job ID"),
    application_status: str | None = Query(None, alias="status", description="Filter by status"),
) -> dict[str, int]:
    """
    Get the total count of applications.

    - **job_seeker_id**: Filter by job seeker profile ID
    - **job_id**: Filter by job ID
    - **application_status**: Filter by application status
    """
    count = await application_crud.get_applications_count(
        job_seeker_id=job_seeker_id, job_id=job_id, status=application_status
    )
    return {"count": count}


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str, current_user: dict = Depends(get_current_user)
) -> ApplicationResponse:
    """
    Get a specific application by ID.

    **Requires:** Authentication
    **Authorization:** Applicant, job poster, or admin only

    - **application_id**: Application ID
    """
    application = await application_crud.get_application_by_id(application_id)

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found",
        )

    # Check authorization
    from app.auth.auth_utils import is_admin, is_job_seeker

    if not is_admin(current_user):
        # Get job seeker profile if user is job seeker
        if is_job_seeker(current_user):
            profile = await profile_crud.get_profile_by_user_id(current_user["id"])
            is_applicant = profile and str(profile["_id"]) == str(application.get("job_seeker_id"))
        else:
            is_applicant = False

        # Check if user is the job poster (employer)
        job = await job_crud.get_job_by_id(str(application.get("job_id")))
        is_job_poster = job and str(job.get("posted_by")) == current_user["id"]

        if not is_applicant and not is_job_poster:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own applications or applications to your jobs",
            )

    return _serialize_application(application)


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    current_user: dict = Depends(get_current_user),
) -> ApplicationResponse:
    """
    Update an application.

    **Requires:** Authentication
    **Authorization:**
    - Job seekers can update their own applications (notes, resume)
    - Employers can update status of applications to their jobs
    - Admins can update any application

    - **application_id**: Application ID
    - Provide only the fields you want to update

    If the status is changed, it will be recorded in the status history.
    """
    # Check if application exists
    existing_application = await application_crud.get_application_by_id(application_id)
    if not existing_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found",
        )

    # Check authorization
    from app.auth.auth_utils import is_admin, is_job_seeker

    if not is_admin(current_user):
        # Get job seeker profile if user is job seeker
        if is_job_seeker(current_user):
            profile = await profile_crud.get_profile_by_user_id(current_user["id"])
            is_applicant = profile and str(profile["_id"]) == str(
                existing_application.get("job_seeker_id")
            )
        else:
            is_applicant = False

        # Check if user is the job poster (employer)
        job = await job_crud.get_job_by_id(str(existing_application.get("job_id")))
        is_job_poster = job and str(job.get("posted_by")) == current_user["id"]

        if not is_applicant and not is_job_poster:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own applications or applications to your jobs",
            )

        # Job seekers can't update status
        if is_applicant and not is_job_poster and application_update.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the employer can update application status",
            )

    # Update the application
    update_data = application_update.model_dump(exclude_unset=True)
    updated_application = await application_crud.update_application(
        application_id, update_data, changed_by=current_user["id"]
    )

    if not updated_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found",
        )

    return _serialize_application(updated_application)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: str, current_user: dict = Depends(get_current_user)
) -> None:
    """
    Delete (withdraw) an application.

    **Requires:** Authentication
    **Authorization:** Only the applicant can withdraw their application (or admin)

    - **application_id**: Application ID
    """
    # Check if application exists
    existing_application = await application_crud.get_application_by_id(application_id)
    if not existing_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found",
        )

    # Check authorization - only applicant or admin can delete
    from app.auth.auth_utils import is_admin

    if not is_admin(current_user):
        # Verify user owns the job seeker profile that applied
        profile = await profile_crud.get_profile_by_user_id(current_user["id"])
        is_applicant = profile and str(profile["_id"]) == str(
            existing_application.get("job_seeker_id")
        )

        if not is_applicant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only withdraw your own applications",
            )

    deleted = await application_crud.delete_application(application_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found",
        )
