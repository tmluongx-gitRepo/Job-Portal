"""Tests for embedding caching utilities."""

from __future__ import annotations

import pytest

from app.ai import embeddings as embeddings_module


class StubRedisClient:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.storage.get(key)

    async def setex(self, key: str, _ttl: int, value: str) -> None:
        self.storage[key] = value


class StubCache:
    def __init__(self) -> None:
        self.client_instance = StubRedisClient()

    async def client(self) -> StubRedisClient:
        return self.client_instance


@pytest.mark.asyncio
async def test_generate_embedding_caches_vector(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = StubCache()

    embeddings_module._get_cache.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(embeddings_module, "_get_cache", lambda: cache)

    text = "Test resume snippet"
    vector_first = await embeddings_module.generate_embedding(text)
    vector_second = await embeddings_module.generate_embedding(text)

    assert vector_first == vector_second
    stored = await cache.client_instance.get(f"embedding:{embeddings_module._hash_text(text)}")
    assert stored is not None
