"""Webhook service for triggering n8n workflows (fire-and-forget)."""

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from app.config import settings
from app.type_definitions import (
    ApplicationDocument,
    InterviewDocument,
    JobDocument,
    JobSeekerProfileDocument,
)

logger = logging.getLogger("app.webhooks")


async def _send_webhook(
    event: str, payload: dict[str, Any], resource_id: str | None = None
) -> None:
    """Send payload to configured webhook endpoint with retries."""

    headers: dict[str, str] | None = None
    if settings.N8N_WEBHOOK_AUTH_HEADER_NAME and settings.N8N_WEBHOOK_AUTH_HEADER_VALUE:
        headers = {settings.N8N_WEBHOOK_AUTH_HEADER_NAME: settings.N8N_WEBHOOK_AUTH_HEADER_VALUE}

    attempts = max(1, settings.WEBHOOK_MAX_RETRIES)
    min_delay = max(0.1, settings.WEBHOOK_RETRY_MIN_DELAY)
    timeout = settings.WEBHOOK_TIMEOUT_SECONDS

    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    settings.N8N_WEBHOOK_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.warning(
                "webhook.timeout",
                extra={
                    "event": event,
                    "resource_id": resource_id,
                    "attempt": attempt + 1,
                    "max_attempts": attempts,
                    "error": str(exc),
                },
            )
        except httpx.HTTPError as exc:
            logger.warning(
                "webhook.http_error",
                extra={
                    "event": event,
                    "resource_id": resource_id,
                    "attempt": attempt + 1,
                    "max_attempts": attempts,
                    "error": str(exc),
                },
            )
        except Exception:
            logger.exception(
                "webhook.unexpected_error",
                extra={"event": event, "resource_id": resource_id},
            )
            return
        else:
            logger.info(
                "webhook.sent",
                extra={"event": event, "resource_id": resource_id},
            )
            return

        if attempt + 1 < attempts:
            await asyncio.sleep(min_delay * (2**attempt))
    logger.error(
        "webhook.failed",
        extra={"event": event, "resource_id": resource_id},
    )


def _serialize_datetime(value: Any) -> Any:
    """Convert datetime objects to ISO format strings."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


async def trigger_application_webhook(
    application: ApplicationDocument,
    job: JobDocument,
    job_seeker: JobSeekerProfileDocument,
) -> None:
    """
    Trigger n8n webhook when a new application is created.

    This sends enriched data to n8n so the workflow doesn't need to
    make additional API calls to fetch job and job seeker details.

    Args:
        application: The created application document
        job: The job being applied to
        job_seeker: The job seeker profile

    Returns:
        None - This is a fire-and-forget operation
    """
    # Skip if webhook is not enabled or URL is not configured
    if not settings.N8N_WEBHOOK_ENABLED or not settings.N8N_WEBHOOK_URL:
        logger.debug("N8N webhook not enabled or URL not configured, skipping")
        return

    payload = {
        "event": "application_created",
        "application": {
            "id": str(application["_id"]),
            "status": application.get("status", "Application Submitted"),
            "applied_date": _serialize_datetime(application.get("applied_date")),
            "notes": application.get("notes"),
        },
        "job": {
            "id": str(job["_id"]),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", ""),
            "description": job.get("description", ""),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
        },
        "job_seeker": {
            "id": str(job_seeker["_id"]),
            "first_name": job_seeker.get("first_name", ""),
            "last_name": job_seeker.get("last_name", ""),
            "email": job_seeker.get("email", ""),
            "phone": job_seeker.get("phone"),
            "location": job_seeker.get("location"),
            "skills": job_seeker.get("skills", []),
            "experience_years": job_seeker.get("experience_years", 0),
        },
    }

    await _send_webhook("application_created", payload, str(application["_id"]))


async def trigger_interview_webhook(
    interview: InterviewDocument,
    job: JobDocument,
    job_seeker: JobSeekerProfileDocument,
    application: ApplicationDocument,
) -> None:
    """
    Trigger n8n webhook when an interview is scheduled.

    This sends enriched data to n8n so the workflow doesn't need to
    make additional API calls to fetch job and job seeker details.

    Args:
        interview: The scheduled interview document
        job: The job for which interview is scheduled
        job_seeker: The job seeker profile
        application: The related application document

    Returns:
        None - This is a fire-and-forget operation
    """
    # Skip if webhook is not enabled or URL is not configured
    if not settings.N8N_WEBHOOK_ENABLED or not settings.N8N_WEBHOOK_URL:
        logger.debug("N8N webhook not enabled or URL not configured, skipping")
        return

    payload = {
        "event": "interview_scheduled",
        "interview": {
            "id": str(interview["_id"]),
            "interview_type": interview.get("interview_type", ""),
            "scheduled_date": _serialize_datetime(interview.get("scheduled_date")),
            "duration_minutes": interview.get("duration_minutes", 60),
            "timezone": interview.get("timezone", ""),
            "location": interview.get("location"),
            "interviewer_name": interview.get("interviewer_name"),
            "interviewer_email": interview.get("interviewer_email"),
            "interviewer_phone": interview.get("interviewer_phone"),
            "notes": interview.get("notes"),
        },
        "job": {
            "id": str(job["_id"]),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", ""),
        },
        "job_seeker": {
            "id": str(job_seeker["_id"]),
            "first_name": job_seeker.get("first_name", ""),
            "last_name": job_seeker.get("last_name", ""),
            "email": job_seeker.get("email", ""),
            "phone": job_seeker.get("phone"),
        },
        "application": {
            "id": str(application["_id"]),
            "status": application.get("status", ""),
        },
    }

    await _send_webhook("interview_scheduled", payload, str(interview["_id"]))


async def trigger_interview_updated_webhook(
    interview: InterviewDocument,
    job: JobDocument,
    job_seeker: JobSeekerProfileDocument,
    application: ApplicationDocument,
    update_type: str = "rescheduled",
) -> None:
    """
    Trigger n8n webhook when an interview is updated/rescheduled.

    This sends enriched data to n8n so the workflow doesn't need to
    make additional API calls to fetch job and job seeker details.

    Args:
        interview: The updated interview document
        job: The job for which interview is scheduled
        job_seeker: The job seeker profile
        application: The related application document
        update_type: Type of update ("rescheduled", "modified", etc.)

    Returns:
        None - This is a fire-and-forget operation
    """
    # Skip if webhook is not enabled or URL is not configured
    if not settings.N8N_WEBHOOK_ENABLED or not settings.N8N_WEBHOOK_URL:
        logger.debug("N8N webhook not enabled or URL not configured, skipping")
        return

    payload = {
        "event": "interview_updated",
        "update_type": update_type,
        "interview": {
            "id": str(interview["_id"]),
            "interview_type": interview.get("interview_type", ""),
            "scheduled_date": _serialize_datetime(interview.get("scheduled_date")),
            "duration_minutes": interview.get("duration_minutes", 60),
            "timezone": interview.get("timezone", ""),
            "location": interview.get("location"),
            "interviewer_name": interview.get("interviewer_name"),
            "interviewer_email": interview.get("interviewer_email"),
            "interviewer_phone": interview.get("interviewer_phone"),
            "notes": interview.get("notes"),
            "status": interview.get("status", ""),
            "rescheduled_from": _serialize_datetime(interview.get("rescheduled_from")),
        },
        "job": {
            "id": str(job["_id"]),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", ""),
        },
        "job_seeker": {
            "id": str(job_seeker["_id"]),
            "first_name": job_seeker.get("first_name", ""),
            "last_name": job_seeker.get("last_name", ""),
            "email": job_seeker.get("email", ""),
            "phone": job_seeker.get("phone"),
        },
        "application": {
            "id": str(application["_id"]),
            "status": application.get("status", ""),
        },
    }

    await _send_webhook("interview_updated", payload, str(interview["_id"]))


async def trigger_application_status_changed_webhook(
    application: ApplicationDocument,
    job: JobDocument,
    job_seeker: JobSeekerProfileDocument,
    old_status: str,
    new_status: str,
) -> None:
    """
    Trigger n8n webhook when an application status is changed.

    This sends enriched data to n8n so the workflow doesn't need to
    make additional API calls to fetch job and job seeker details.

    Args:
        application: The updated application document
        job: The job being applied to
        job_seeker: The job seeker profile
        old_status: Previous application status
        new_status: New application status

    Returns:
        None - This is a fire-and-forget operation
    """
    # Skip if webhook is not enabled or URL is not configured
    if not settings.N8N_WEBHOOK_ENABLED or not settings.N8N_WEBHOOK_URL:
        logger.debug("N8N webhook not enabled or URL not configured, skipping")
        return

    payload = {
        "event": "application_status_changed",
        "old_status": old_status,
        "new_status": new_status,
        "application": {
            "id": str(application["_id"]),
            "status": application.get("status", ""),
            "applied_date": _serialize_datetime(application.get("applied_date")),
            "notes": application.get("notes"),
            "next_step": application.get("next_step"),
            "rejection_reason": application.get("rejection_reason"),
        },
        "job": {
            "id": str(job["_id"]),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "job_type": job.get("job_type", ""),
        },
        "job_seeker": {
            "id": str(job_seeker["_id"]),
            "first_name": job_seeker.get("first_name", ""),
            "last_name": job_seeker.get("last_name", ""),
            "email": job_seeker.get("email", ""),
            "phone": job_seeker.get("phone"),
        },
    }

    await _send_webhook("application_status_changed", payload, str(application["_id"]))
