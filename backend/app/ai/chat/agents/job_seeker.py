"""LangChain v1 agent that handles job seeker conversations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.ai.chat.chain import job_seeker_response, job_seeker_stream
from app.ai.chat.constants import ChatEventType


class JobSeekerAgent:
    """LangChain-backed agent focused on job seeker interactions."""

    async def stream(
        self, message: str, context: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], str, AsyncIterator[str]]:
        matches, summary, factory = await job_seeker_stream(message, context)
        return list(matches), summary, factory()

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the job seeker conversation."""

        payload = await job_seeker_response(message, context)
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
