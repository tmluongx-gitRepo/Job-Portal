"""Monitoring helpers for the chat subsystem."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger("app.ai.chat")


def configure_tracing() -> None:
    """Ensure LangSmith tracing is configured when enabled in settings."""

    if not settings.LANGCHAIN_TRACING_ENABLED:
        return

    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    if settings.LANGCHAIN_PROJECT:
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.LANGCHAIN_PROJECT)


@contextmanager
def tracing_context(operation: str) -> Iterator[None]:
    """Context manager that activates LangSmith tracing when requested.

    An empty ``operation`` name will disable tracing for the block and emit a
    warning so misconfigurations are surfaced during development.
    """

    if not settings.LANGCHAIN_TRACING_ENABLED:
        yield
        return

    if not operation:
        logger.warning("tracing.operation_missing", extra={"operation": operation})
        yield
        return

    try:
        from langchain_core.tracers.context import tracing_v2_enabled
    except ImportError:  # pragma: no cover - optional dependency
        yield
        return

    with tracing_v2_enabled(session_name=operation):  # type: ignore[call-arg]
        yield
