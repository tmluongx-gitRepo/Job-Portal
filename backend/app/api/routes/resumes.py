"""Resume API routes with automatic embedding ingestion hooks."""

import asyncio
import contextlib
import io
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.auth.auth_utils import is_admin
from app.auth.dependencies import get_current_user, require_job_seeker
from app.crud import resume as resume_crud
from app.schemas.resume import ResumeMetadataResponse, ResumeUploadResponse
from app.tasks.embedding_tasks import process_candidates, remove_candidates
from app.type_definitions import ResumeDocument
from app.utils.dropbox_utils import get_dropbox_service

router = APIRouter()

logger = logging.getLogger(__name__)

# File validation constants
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/msword",  # .doc
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _serialize_resume_upload(document: ResumeDocument) -> ResumeUploadResponse:
    """Convert a database document to the upload response schema."""
    return ResumeUploadResponse(
        id=str(document["_id"]),
        job_seeker_id=document["job_seeker_id"],
        original_filename=document["original_filename"],
        dropbox_path=document["dropbox_path"],
        uploaded_at=document["uploaded_at"],
        content_type=document["content_type"],
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _serialize_resume_metadata(document: ResumeDocument) -> ResumeMetadataResponse:
    """Convert a database document to the metadata response schema."""
    return ResumeMetadataResponse(
        id=str(document["_id"]),
        original_filename=document["original_filename"],
        uploaded_at=document["uploaded_at"],
        content_type=document["content_type"],
    )


@router.post("", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...), job_seeker: dict = Depends(require_job_seeker)
) -> ResumeUploadResponse:
    """
    Upload a resume file.

    **Requires:** Job Seeker account

    **Validation:**
    - File types: PDF, DOCX, DOC
    - Max size: 5MB

    The resume will be stored in Dropbox and metadata saved in MongoDB.
    If a resume already exists, it will be replaced.
    """
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed types: PDF, DOCX, DOC",
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size: 5MB",
        )

    # Get Dropbox service
    dropbox_service = get_dropbox_service()

    try:
        # Delete old resume from Dropbox if it exists
        old_resume = await resume_crud.get_resume_by_job_seeker(job_seeker["id"])
        if old_resume:
            with contextlib.suppress(Exception):
                # Continue even if old file deletion fails
                dropbox_service.delete_file(old_resume["dropbox_path"])

        # Upload to Dropbox
        dropbox_path = dropbox_service.upload_file(file_content, job_seeker["id"])

        # Save metadata to MongoDB
        resume = await resume_crud.create_or_update_resume(
            job_seeker_id=job_seeker["id"],
            dropbox_path=dropbox_path,
            original_filename=file.filename or "resume.pdf",
            content_type=file.content_type or "application/pdf",
        )

        _schedule_candidate_embedding(job_seeker["id"])

        return _serialize_resume_upload(resume)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/me", response_model=ResumeMetadataResponse)
async def get_my_resume(
    job_seeker: dict = Depends(require_job_seeker),
) -> ResumeMetadataResponse:
    """
    Get metadata for your own resume.

    **Requires:** Job Seeker account

    Returns resume metadata without downloading the file.
    """
    resume = await resume_crud.get_resume_by_job_seeker(job_seeker["id"])

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found. Please upload a resume first.",
        )

    return _serialize_resume_metadata(resume)


def _schedule_candidate_embedding(candidate_id: str) -> None:
    async def _runner() -> None:
        try:
            await process_candidates([candidate_id])
        except Exception:  # pragma: no cover - background defensive logging
            logger.exception(
                "resume.embedding_ingest_failed",
                extra={"candidate_id": candidate_id},
            )

    asyncio.create_task(_runner())  # noqa: RUF006


def _schedule_candidate_removal(candidate_id: str) -> None:
    async def _runner() -> None:
        try:
            await remove_candidates([candidate_id])
        except Exception:  # pragma: no cover - background defensive logging
            logger.exception(
                "resume.embedding_delete_failed",
                extra={"candidate_id": candidate_id},
            )

    asyncio.create_task(_runner())  # noqa: RUF006


@router.get("/{resume_id}", response_model=ResumeMetadataResponse)
async def get_resume(
    resume_id: str, current_user: dict = Depends(get_current_user)
) -> ResumeMetadataResponse:
    """
    Get resume metadata by ID.

    **Requires:** Authentication
    **Authorization:** Owner or admin only
    """
    resume = await resume_crud.get_resume_by_id(resume_id)

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found",
        )

    # Check ownership
    if not is_admin(current_user) and resume["job_seeker_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only access your own resume"
        )

    return _serialize_resume_metadata(resume)


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str, current_user: dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    Download resume file.

    **Requires:** Authentication
    **Authorization:** Owner or admin only

    Returns the resume file as a download.
    """
    resume = await resume_crud.get_resume_by_id(resume_id)

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found",
        )

    # Check ownership
    if not is_admin(current_user) and resume["job_seeker_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only download your own resume"
        )

    # Download from Dropbox
    dropbox_service = get_dropbox_service()

    try:
        file_content = dropbox_service.download_file(resume["dropbox_path"])
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found in storage"
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=resume["content_type"],
        headers={"Content-Disposition": f'attachment; filename="{resume["original_filename"]}"'},
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_resume(job_seeker: dict = Depends(require_job_seeker)) -> None:
    """
    Delete your own resume.

    **Requires:** Job Seeker account

    Deletes the resume from both Dropbox and MongoDB.
    """
    resume = await resume_crud.get_resume_by_job_seeker(job_seeker["id"])

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found. Nothing to delete.",
        )

    # Delete from Dropbox
    dropbox_service = get_dropbox_service()
    with contextlib.suppress(Exception):
        # Continue even if Dropbox deletion fails
        dropbox_service.delete_file(resume["dropbox_path"])

    # Delete from MongoDB
    success = await resume_crud.delete_resume(job_seeker["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume metadata",
        )

    _schedule_candidate_removal(job_seeker["id"])
