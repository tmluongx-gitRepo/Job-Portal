"""
API routes for interview scheduling.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_utils import is_admin, is_employer, is_job_seeker
from app.auth.dependencies import get_current_user
from app.constants import ApplicationStatus
from app.crud import application as application_crud
from app.crud import interview as interview_crud
from app.crud import job as job_crud
from app.crud import job_seeker_profile as job_seeker_profile_crud
from app.schemas.interview import (
    InterviewCancel,
    InterviewComplete,
    InterviewCreate,
    InterviewListResponse,
    InterviewResponse,
    InterviewUpdate,
)
from app.services.webhook_service import trigger_interview_webhook, trigger_interview_updated_webhook

router = APIRouter(tags=["Interviews"])


def _serialize_interview(interview: dict, current_user: dict | None = None) -> dict:
    """
    Serialize interview document for API response with role-based filtering.

    Args:
        interview: Interview document from MongoDB
        current_user: Current authenticated user (for role-based filtering)

    Returns:
        Serialized interview dictionary with appropriate fields based on user role
    """
    # Base serialization
    serialized = {
        "id": str(interview["_id"]),
        "application_id": interview["application_id"],
        "job_id": interview["job_id"],
        "job_seeker_id": interview["job_seeker_id"],
        "employer_id": interview["employer_id"],
        "interview_type": interview["interview_type"],
        "scheduled_date": interview["scheduled_date"],
        "duration_minutes": interview["duration_minutes"],
        "timezone": interview["timezone"],
        "location": interview.get("location"),
        "interviewer_name": interview.get("interviewer_name"),
        "interviewer_email": interview.get("interviewer_email"),
        "interviewer_phone": interview.get("interviewer_phone"),
        "notes": interview.get("notes"),  # Public notes visible to job seekers
        "status": interview["status"].title()
        if isinstance(interview.get("status"), str)
        else interview["status"],  # Normalize to title case for backward compatibility
        "reminder_sent": interview.get("reminder_sent", False),
        "cancelled_by": interview.get("cancelled_by"),
        "cancelled_reason": interview.get("cancelled_reason"),
        "rescheduled_from": interview.get("rescheduled_from"),
        "created_at": interview["created_at"],
        "updated_at": interview["updated_at"],
        # Populated fields
        "job_title": interview.get("job_title"),
        "company": interview.get("company"),
    }

    # Role-based field inclusion to prevent information leakage
    if current_user:
        is_employer_or_admin = is_employer(current_user) or is_admin(current_user)

        # Internal notes: Only visible to employers and admins
        if is_employer_or_admin:
            serialized["internal_notes"] = interview.get("internal_notes")
            # Feedback and rating: Only visible to employers and admins
            serialized["feedback"] = interview.get("feedback")
            serialized["rating"] = interview.get("rating")
            # Job seeker contact info: Only visible to employers and admins
            serialized["job_seeker_name"] = interview.get("job_seeker_name")
            serialized["job_seeker_email"] = interview.get("job_seeker_email")
        else:
            # Job seekers don't see internal notes, feedback, or rating
            serialized["internal_notes"] = None
            serialized["feedback"] = None
            serialized["rating"] = None
            # Job seekers can see their own name (populated from their profile)
            serialized["job_seeker_name"] = interview.get("job_seeker_name")
            serialized["job_seeker_email"] = None  # Don't leak email
    else:
        # No user context - return minimal sensitive data
        serialized["internal_notes"] = None
        serialized["feedback"] = None
        serialized["rating"] = None
        serialized["job_seeker_name"] = None
        serialized["job_seeker_email"] = None

    return serialized


async def _serialize_interviews(interviews: list, current_user: dict | None = None) -> list[dict]:
    """
    Serialize multiple interview documents for API response.

    Args:
        interviews: List of interview documents from MongoDB
        current_user: Current authenticated user (for role-based filtering)

    Returns:
        List of serialized interview dictionaries with populated details
    """
    serialized = []
    for interview in interviews:
        interview_dict = dict(interview)
        interview_dict = await _populate_interview_details(interview_dict)
        serialized.append(_serialize_interview(interview_dict, current_user))
    return serialized


async def _populate_interview_details(interview: dict) -> dict:
    """
    Populate interview with job and job seeker details.

    Args:
        interview: Interview document

    Returns:
        Interview with populated fields
    """
    # Get job details
    job = await job_crud.get_job_by_id(interview["job_id"])
    if job:
        interview["job_title"] = job.get("title")
        interview["company"] = job.get("company")

    # Get job seeker details
    job_seeker = await job_seeker_profile_crud.get_profile_by_id(interview["job_seeker_id"])
    if job_seeker:
        first_name = job_seeker.get("first_name", "")
        last_name = job_seeker.get("last_name", "")
        interview["job_seeker_name"] = f"{first_name} {last_name}".strip()
        interview["job_seeker_email"] = job_seeker.get("email")

    return interview


@router.post("", status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    interview_data: InterviewCreate, current_user: dict = Depends(get_current_user)
) -> InterviewResponse:
    """
    Schedule a new interview for an application.

    **Requires:** Authentication (Employer or Admin)
    **Authorization:** Only the employer who posted the job can schedule interviews
    """
    # Only employers and admins can schedule interviews
    if not is_employer(current_user) and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can schedule interviews",
        )

    # Get the application
    application = await application_crud.get_application_by_id(interview_data.application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {interview_data.application_id} not found",
        )

    # Get the job to verify ownership
    job = await job_crud.get_job_by_id(application["job_id"])
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Check if user is the job owner or admin
    # Ensure posted_by is always a string for comparison
    job_posted_by = str(job.get("posted_by", ""))
    if not is_admin(current_user) and job_posted_by != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only schedule interviews for your own job postings",
        )

    # Check if interview already exists for this application
    existing_interview = await interview_crud.get_interview_by_application_id(
        interview_data.application_id
    )
    if existing_interview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview already scheduled for this application",
        )

    # Create the interview - ensure IDs are strings for type safety
    try:
        interview = await interview_crud.create_interview(
            application_id=interview_data.application_id,
            job_id=str(application["job_id"]),
            job_seeker_id=str(application["job_seeker_id"]),
            employer_id=current_user["id"],
            interview_type=interview_data.interview_type,
            scheduled_date=interview_data.scheduled_date,
            duration_minutes=interview_data.duration_minutes,
            timezone=interview_data.timezone,
            location=interview_data.location,
            interviewer_name=interview_data.interviewer_name,
            interviewer_email=str(interview_data.interviewer_email)
            if interview_data.interviewer_email
            else None,
            interviewer_phone=interview_data.interviewer_phone,
            notes=interview_data.notes,
            internal_notes=interview_data.internal_notes,
        )
    except ValueError as e:
        # DuplicateKeyError caught in CRUD - race condition
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None

    # Update application with interview date
    await application_crud.update_application(
        interview_data.application_id,
        {
            "interview_scheduled_date": interview_data.scheduled_date,
            "status": "interview_scheduled",
            "next_step": f"{interview_data.interview_type.title()} interview scheduled",
        },
    )

    # Fetch job seeker profile for webhook
    job_seeker_profile = await job_seeker_profile_crud.get_profile_by_id(
        str(application["job_seeker_id"])
    )

    # Trigger n8n webhook asynchronously (fire-and-forget)
    # We have job, application already; just fetched job_seeker_profile
    if job_seeker_profile:
        asyncio.create_task(
            trigger_interview_webhook(interview, job, job_seeker_profile, application)
        )

    # Populate details and return
    interview_dict = dict(interview)
    interview_dict = await _populate_interview_details(interview_dict)
    return InterviewResponse(**_serialize_interview(interview_dict, current_user))


@router.get("")
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    upcoming_only: bool = Query(False, description="Only show upcoming interviews"),
    current_user: dict = Depends(get_current_user),
) -> InterviewListResponse:
    """
    List interviews.

    **Requires:** Authentication
    **Authorization:**
    - Job seekers: See only their own interviews
    - Employers: See interviews for their jobs
    - Admins: See all interviews
    """
    if is_admin(current_user):
        # Admins see all interviews
        interviews = await interview_crud.get_interviews(
            skip=skip,
            limit=limit,
            status=status_filter,
            upcoming_only=upcoming_only,
        )
        total = await interview_crud.count_interviews(status=status_filter)
    elif is_job_seeker(current_user):
        # Job seekers see their own interviews
        # Get their job seeker profile
        profile = await job_seeker_profile_crud.get_profile_by_user_id(current_user["id"])
        if not profile:
            return InterviewListResponse(interviews=[], total=0)

        interviews = await interview_crud.get_interviews(
            skip=skip,
            limit=limit,
            job_seeker_id=str(profile["_id"]),
            status=status_filter,
            upcoming_only=upcoming_only,
        )
        total = await interview_crud.count_interviews(
            job_seeker_id=str(profile["_id"]),
            status=status_filter,
        )
    elif is_employer(current_user):
        # Employers see interviews for their jobs
        interviews = await interview_crud.get_interviews(
            skip=skip,
            limit=limit,
            employer_id=current_user["id"],
            status=status_filter,
            upcoming_only=upcoming_only,
        )
        total = await interview_crud.count_interviews(
            employer_id=current_user["id"],
            status=status_filter,
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid account type")

    # Serialize interviews with populated details
    serialized = await _serialize_interviews(interviews, current_user)
    return InterviewListResponse(
        interviews=[InterviewResponse(**i) for i in serialized],
        total=total,
    )


@router.get("/upcoming")
async def list_upcoming_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
) -> InterviewListResponse:
    """
    List upcoming interviews (scheduled or rescheduled, in the future).

    **Requires:** Authentication
    **Authorization:** Same as list_interviews
    """
    return await list_interviews(  # type: ignore[no-any-return]
        skip=skip,
        limit=limit,
        status_filter=None,
        upcoming_only=True,
        current_user=current_user,
    )


@router.get("/{interview_id}")
async def get_interview(
    interview_id: str, current_user: dict = Depends(get_current_user)
) -> InterviewResponse:
    """
    Get interview details.

    **Requires:** Authentication
    **Authorization:**
    - Job seekers: Can view their own interviews
    - Employers: Can view interviews for their jobs
    - Admins: Can view all interviews
    """
    interview = await interview_crud.get_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Check authorization
    can_view = False
    if is_admin(current_user):
        can_view = True
    elif is_employer(current_user):
        # Employer can view interviews for their jobs
        if interview["employer_id"] == current_user["id"]:
            can_view = True
    elif is_job_seeker(current_user):
        # Job seeker can view their own interviews
        profile = await job_seeker_profile_crud.get_profile_by_user_id(current_user["id"])
        if profile and str(profile["_id"]) == interview["job_seeker_id"]:
            can_view = True

    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this interview",
        )

    # Populate details and return
    interview_dict = dict(interview)
    interview_dict = await _populate_interview_details(interview_dict)
    return InterviewResponse(**_serialize_interview(interview_dict, current_user))


@router.put("/{interview_id}")
async def update_interview(
    interview_id: str,
    update_data: InterviewUpdate,
    current_user: dict = Depends(get_current_user),
) -> InterviewResponse:
    """
    Update an interview (reschedule or modify details).

    **Requires:** Authentication (Employer or Admin)
    **Authorization:** Only the employer who owns the job can update interviews
    """
    interview = await interview_crud.get_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Check authorization
    can_update = is_admin(current_user) or (
        is_employer(current_user) and interview["employer_id"] == current_user["id"]
    )

    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this interview",
        )

    # Update the interview
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_interview = await interview_crud.update_interview(interview_id, update_dict)

    if not updated_interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Determine update type
    update_type = "rescheduled" if "scheduled_date" in update_dict else "modified"

    # If rescheduled, update application
    if "scheduled_date" in update_dict:
        await application_crud.update_application(
            interview["application_id"],
            {
                "interview_scheduled_date": update_dict["scheduled_date"],
                "next_step": "Interview rescheduled",
            },
        )

    # Fetch related data for webhook
    job = await job_crud.get_job_by_id(updated_interview["job_id"])
    application = await application_crud.get_application_by_id(updated_interview["application_id"])
    job_seeker_profile = await job_seeker_profile_crud.get_profile_by_id(
        updated_interview["job_seeker_id"]
    )

    # Trigger n8n webhook asynchronously (fire-and-forget)
    if job and application and job_seeker_profile:
        asyncio.create_task(
            trigger_interview_updated_webhook(
                updated_interview, job, job_seeker_profile, application, update_type
            )
        )

    # Populate details and return
    interview_dict = dict(updated_interview)
    interview_dict = await _populate_interview_details(interview_dict)
    return InterviewResponse(**_serialize_interview(interview_dict, current_user))


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_interview(
    interview_id: str,
    cancellation_data: InterviewCancel,
    current_user: dict = Depends(get_current_user),
) -> None:
    """
    Cancel an interview.

    **Requires:** Authentication
    **Authorization:**
    - Employers: Can cancel interviews for their jobs
    - Job seekers: Can cancel their own interviews
    - Admins: Can cancel any interview
    """
    interview = await interview_crud.get_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Check authorization
    can_cancel = False
    if is_admin(current_user):
        can_cancel = True
    elif is_employer(current_user):
        # Employer can cancel interviews for their jobs
        if interview["employer_id"] == current_user["id"]:
            can_cancel = True
    elif is_job_seeker(current_user):
        # Job seeker can cancel their own interviews
        profile = await job_seeker_profile_crud.get_profile_by_user_id(current_user["id"])
        if profile and str(profile["_id"]) == interview["job_seeker_id"]:
            can_cancel = True

    if not can_cancel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this interview",
        )

    # Cancel the interview
    await interview_crud.cancel_interview(
        interview_id,
        cancelled_by=current_user["id"],
        reason=cancellation_data.reason,
    )

    # Update application status to reflect cancellation
    await application_crud.update_application(
        interview["application_id"],
        {
            "status": "interview_cancelled",  # Update status for better tracking
            "interview_scheduled_date": None,
            "next_step": "Interview cancelled",
        },
    )


@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    completion_data: InterviewComplete,
    current_user: dict = Depends(get_current_user),
) -> InterviewResponse:
    """
    Mark an interview as complete and add feedback.

    **Requires:** Authentication (Employer or Admin)
    **Authorization:** Only the employer who owns the job can complete interviews
    """
    interview = await interview_crud.get_interview_by_id(interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Check authorization
    can_complete = is_admin(current_user) or (
        is_employer(current_user) and interview["employer_id"] == current_user["id"]
    )

    if not can_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to complete this interview",
        )

    # Complete the interview
    updated_interview = await interview_crud.complete_interview(
        interview_id,
        feedback=completion_data.feedback,
        rating=completion_data.rating,
    )

    if not updated_interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Update application status
    update_data: dict[str, object] = {
        "status": ApplicationStatus.INTERVIEWED.value,
        "next_step": completion_data.next_step or "Awaiting decision",
    }
    await application_crud.update_application(interview["application_id"], update_data)

    # Populate details and return
    interview_dict = dict(updated_interview)
    interview_dict = await _populate_interview_details(interview_dict)
    return InterviewResponse(**_serialize_interview(interview_dict, current_user))
