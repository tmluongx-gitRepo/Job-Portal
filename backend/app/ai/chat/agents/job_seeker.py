"""LangChain v1 agent that handles job seeker conversations."""

from __future__ import annotations

from typing import Any

from app.ai.chat.chain import job_seeker_response
from app.ai.chat.constants import ChatEventType


class JobSeekerAgent:
    """LangChain-backed agent focused on job seeker interactions."""

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the job seeker conversation."""

        payload = await job_seeker_response(message, context)
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
