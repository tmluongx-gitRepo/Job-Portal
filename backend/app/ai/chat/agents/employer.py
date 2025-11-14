"""LangChain v1 agent that handles employer conversations."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable

from app.ai.chat.chain import build_employer_chain
from app.ai.chat.constants import ChatEventType


class EmployerAgent:
    """LangChain-backed agent for employer oriented conversations."""

    def __init__(self, *, chain: Runnable[dict[str, Any], dict[str, Any]] | None = None) -> None:
        self._chain = chain or build_employer_chain()

    async def generate(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return structured data notes for the employer conversation."""

        payload = await self._chain.ainvoke({"message": message, "context": context})
        return {
            "type": ChatEventType.TOKEN.value,
            "data": payload,
        }
