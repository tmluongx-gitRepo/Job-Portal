"""
Saved Jobs API routes.
"""

from collections.abc import Iterable

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_utils import is_admin
from app.auth.dependencies import get_current_user, require_job_seeker
from app.crud import saved_job as saved_job_crud
from app.schemas.saved_job import SavedJobCreate, SavedJobResponse, SavedJobUpdate
from app.type_definitions import SavedJobDocument

router = APIRouter()


def _serialize_saved_job(document: SavedJobDocument) -> SavedJobResponse:
    """Convert a database document to the response schema."""
    job_seeker_id = document.get("job_seeker_id", "")
    job_id = document.get("job_id", "")
    notes = document.get("notes")
    saved_date = document["saved_date"]
    created_at = document["created_at"]

    return SavedJobResponse(
        id=str(document["_id"]),
        job_seeker_id=job_seeker_id,
        job_id=job_id,
        notes=notes,
        saved_date=saved_date,
        created_at=created_at,
    )


def _serialize_saved_jobs(
    documents: Iterable[SavedJobDocument],
) -> list[SavedJobResponse]:
    """Convert multiple saved job documents into API response schemas."""
    return [_serialize_saved_job(doc) for doc in documents]


@router.post("", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
async def save_job(
    saved_job: SavedJobCreate, job_seeker: dict = Depends(require_job_seeker)
) -> SavedJobResponse:
    """
    Save a job for later viewing.

    **Requires:** Job Seeker account

    The saved job will be automatically linked to the authenticated job seeker.
    """
    try:
        # Use authenticated user's ID
        created_saved_job = await saved_job_crud.create_saved_job(
            job_seeker_id=job_seeker["id"],
            job_id=saved_job.job_id,
            notes=saved_job.notes,
        )

        return _serialize_saved_job(created_saved_job)
    except ValueError as e:
        if "already saved" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("", response_model=list[SavedJobResponse])
async def list_saved_jobs(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of saved jobs to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of saved jobs to return"),
) -> list[SavedJobResponse]:
    """
    Get all saved jobs for the authenticated user.

    **Requires:** Authentication

    **Authorization:**
    - Job seekers see their own saved jobs
    - Admins can see all saved jobs (if job_seeker_id is provided)
    """
    # Determine which job seeker's saved jobs to fetch
    # For now, all users (including admins) see only their own saved jobs
    job_seeker_id = current_user["id"]

    saved_jobs = await saved_job_crud.get_saved_jobs(
        job_seeker_id=job_seeker_id, skip=skip, limit=limit
    )

    return _serialize_saved_jobs(saved_jobs)


@router.get("/check/{job_id}")
async def check_if_job_saved(
    job_id: str, current_user: dict = Depends(get_current_user)
) -> dict[str, bool]:
    """
    Check if a job is already saved by the authenticated user.

    **Requires:** Authentication

    Returns:
        {"is_saved": true/false}
    """
    is_saved = await saved_job_crud.check_if_job_saved(
        job_seeker_id=current_user["id"], job_id=job_id
    )

    return {"is_saved": is_saved}


@router.get("/count")
async def count_saved_jobs(current_user: dict = Depends(get_current_user)) -> dict[str, int]:
    """
    Count the number of saved jobs for the authenticated user.

    **Requires:** Authentication
    """
    count = await saved_job_crud.count_saved_jobs(job_seeker_id=current_user["id"])

    return {"count": count}


@router.get("/{saved_job_id}", response_model=SavedJobResponse)
async def get_saved_job(
    saved_job_id: str, current_user: dict = Depends(get_current_user)
) -> SavedJobResponse:
    """
    Get a specific saved job by ID.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    saved_job = await saved_job_crud.get_saved_job_by_id(saved_job_id)

    if not saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved job with id {saved_job_id} not found",
        )

    # Check ownership
    if not is_admin(current_user) and saved_job.get("job_seeker_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own saved jobs",
        )

    return _serialize_saved_job(saved_job)


@router.put("/{saved_job_id}", response_model=SavedJobResponse)
async def update_saved_job(
    saved_job_id: str,
    saved_job_update: SavedJobUpdate,
    current_user: dict = Depends(get_current_user),
) -> SavedJobResponse:
    """
    Update a saved job (e.g., update notes).

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing saved job
    existing_saved_job = await saved_job_crud.get_saved_job_by_id(saved_job_id)

    if not existing_saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved job with id {saved_job_id} not found",
        )

    # Check ownership
    if not is_admin(current_user) and existing_saved_job.get("job_seeker_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own saved jobs",
        )

    # Update saved job
    update_data = saved_job_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updated_saved_job = await saved_job_crud.update_saved_job(saved_job_id, update_data)

    if not updated_saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved job with id {saved_job_id} not found",
        )

    return _serialize_saved_job(updated_saved_job)


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_job(
    saved_job_id: str, current_user: dict = Depends(get_current_user)
) -> None:
    """
    Remove a saved job.

    **Requires:** Authentication
    **Authorization:** Owner only (or admin)
    """
    # Get existing saved job
    existing_saved_job = await saved_job_crud.get_saved_job_by_id(saved_job_id)

    if not existing_saved_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved job with id {saved_job_id} not found",
        )

    # Check ownership
    if not is_admin(current_user) and existing_saved_job.get("job_seeker_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own saved jobs",
        )

    # Delete saved job
    success = await saved_job_crud.delete_saved_job(saved_job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved job with id {saved_job_id} not found",
        )
