"""LangChain v1 agent that handles job seeker conversations."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda  # type: ignore[import-not-found]

from app.ai.chat.chain import build_job_seeker_chain
from app.ai.chat.constants import ChatEventType


class JobSeekerAgent:
    """LangChain-backed agent focused on job seeker interactions."""

    def __init__(self, *, chain: RunnableLambda | None = None) -> None:
        self._chain = chain or build_job_seeker_chain()

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the job seeker conversation."""

        payload = await self._chain.ainvoke({"message": message, "context": context})
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
