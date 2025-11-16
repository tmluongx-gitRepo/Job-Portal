"""Redis-based caching helpers for chat sessions (scaffold).

The module caches a single RedisChatCache instance per Python process. In multi-worker
deployments (e.g. gunicorn with multiple workers) each worker process will naturally obtain
its own connection, but threaded access within a process is not guarded. If the runtime model
changes, favour explicit dependency injection instead of relying on the singleton below.
"""

from __future__ import annotations

from redis import asyncio as aioredis

from app.config import settings


class RedisChatCache:
    """Convenience wrapper around Redis operations used by the chat agents."""

    def __init__(self) -> None:
        self._client: aioredis.Redis | None = None
        parts = [settings.REDIS_KEY_PREFIX, settings.APP_ENV]
        self._namespace = ":".join(part.strip().lower().replace(" ", "-") for part in parts if part)
        if not self._namespace:
            self._namespace = "chat"

    async def client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()  # type: ignore[attr-defined]
            self._client = None

    async def get_summary(self, *, session_id: str) -> str | None:
        client = await self.client()
        return await client.get(self._summary_key(session_id))

    async def set_summary(self, *, session_id: str, summary: str) -> None:
        client = await self.client()
        await client.setex(
            self._summary_key(session_id),
            settings.CHAT_SESSION_TTL_SECONDS,
            summary,
        )

    async def get_recent_messages(self, *, session_id: str) -> list[str]:
        client = await self.client()
        return await client.lrange(
            self._recent_key(session_id), -settings.CHAT_RECENT_MESSAGE_LIMIT, -1
        )

    async def push_recent_message(self, *, session_id: str, payload: str) -> None:
        client = await self.client()
        key = self._recent_key(session_id)
        async with client.pipeline(transaction=True) as pipe:  # type: ignore[attr-defined]
            await pipe.rpush(key, payload)
            await pipe.ltrim(key, -settings.CHAT_RECENT_MESSAGE_LIMIT, -1)
            await pipe.expire(key, settings.CHAT_SESSION_TTL_SECONDS)
            await pipe.execute()

    def _summary_key(self, session_id: str) -> str:
        return f"{self._namespace}:chat:session:{session_id}:summary"

    def _recent_key(self, session_id: str) -> str:
        return f"{self._namespace}:chat:session:{session_id}:recent"


# Singleton convenience accessor
_chat_cache: RedisChatCache | None = None


def get_chat_cache() -> RedisChatCache:
    """Return the process-local RedisChatCache singleton."""
    global _chat_cache
    if _chat_cache is None:
        _chat_cache = RedisChatCache()
    return _chat_cache


async def shutdown_chat_cache() -> None:
    """Close the shared Redis connection if it was created."""

    global _chat_cache
    if _chat_cache is None:
        return
    try:
        await _chat_cache.close()
    finally:
        _chat_cache = None
