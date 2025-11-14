"""Helper utilities for chat orchestrator scaffolding."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.ai.chat.constants import ChatEventType


async def emit_text(message: str) -> AsyncIterator[dict]:
    """Yield a single text event (non-streaming placeholder)."""
    yield {"type": ChatEventType.TOKEN.value, "data": {"text": message}}
    yield {"type": ChatEventType.COMPLETE.value, "data": {}}
