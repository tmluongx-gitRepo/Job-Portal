"""Tests ensuring RedisChatCache trimming behaviour using a fake pipeline."""

from __future__ import annotations

import pytest

from app.ai.chat.cache import RedisChatCache
from app.config import settings


class FakePipeline:
    def __init__(self, redis: FakeRedis, key: str) -> None:
        self.redis = redis
        self.key = key
        self._ops: list[tuple[str, tuple]] = []

    async def __aenter__(self) -> FakePipeline:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def rpush(self, key: str, payload: str) -> None:
        self._ops.append(("rpush", (key, payload)))

    async def ltrim(self, key: str, start: int, end: int) -> None:
        self._ops.append(("ltrim", (key, start, end)))

    async def expire(self, key: str, ttl: int) -> None:
        self._ops.append(("expire", (key, ttl)))

    async def execute(self) -> None:
        for op, params in self._ops:
            if op == "rpush":
                self.redis._rpush(*params)
            elif op == "ltrim":
                self.redis._ltrim(*params)
            elif op == "expire":
                self.redis._expire(*params)
        self._ops.clear()


class FakeRedis:
    def __init__(self) -> None:
        self.lists: dict[str, list[str]] = {}
        self.expirations: dict[str, int] = {}

    async def get(self, _key: str) -> None:
        return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.lists[key] = [value]
        self.expirations[key] = ttl

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        items = self.lists.get(key, [])
        end_index: int | None
        if end == -1:
            end_index = None  # slice to end
        else:
            end_index = end + 1
        return items[start:end_index]

    def pipeline(self, transaction: bool = True) -> FakePipeline:  # noqa: ARG002
        return FakePipeline(self, "")

    def _rpush(self, key: str, payload: str) -> None:
        self.lists.setdefault(key, []).append(payload)

    def _ltrim(self, key: str, start: int, end: int) -> None:
        items = self.lists.get(key, [])
        end_index: int | None = None if end == -1 else end + 1
        self.lists[key] = items[start:end_index]

    def _expire(self, key: str, ttl: int) -> None:
        self.expirations[key] = ttl


@pytest.mark.asyncio
async def test_push_recent_message_trims_history(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = RedisChatCache()
    fake_redis = FakeRedis()
    object.__setattr__(cache, "_client", fake_redis)

    monkeypatch.setattr(settings, "CHAT_RECENT_MESSAGE_LIMIT", 3)

    for i in range(6):
        await cache.push_recent_message(session_id="session1", payload=str(i))

    items = await cache.get_recent_messages(session_id="session1")
    assert items == ["3", "4", "5"]
    assert fake_redis.expirations["chat:session:session1:recent"] > 0
