"""Utilities for generating and caching OpenAI embeddings."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from functools import lru_cache

from app.ai.chat.cache import RedisChatCache, get_chat_cache
from app.config import settings

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:  # pragma: no cover - optional dependency
    OpenAIEmbeddings = None  # type: ignore[assignment]


_CACHE_NAMESPACE = "embedding"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def _get_cache() -> RedisChatCache:
    return get_chat_cache()


async def _get_cached_vector(text: str) -> list[float] | None:
    cache = _get_cache()
    key = f"{_CACHE_NAMESPACE}:{_hash_text(text)}"
    client = await cache.client()
    raw = await client.get(key)
    if not raw:
        return None
    try:
        result = json.loads(raw)
        return list(result) if isinstance(result, list) else None
    except json.JSONDecodeError:  # pragma: no cover
        return None


async def _store_vector(text: str, vector: Sequence[float]) -> None:
    cache = _get_cache()
    key = f"{_CACHE_NAMESPACE}:{_hash_text(text)}"
    client = await cache.client()
    await client.setex(key, settings.CHAT_SESSION_TTL_SECONDS, json.dumps(list(vector)))


async def generate_embedding(text: str) -> list[float]:
    """Return embedding for text, caching in Redis when possible."""

    text = text.strip()
    if not text:
        return []

    cached = await _get_cached_vector(text)
    if cached is not None:
        return cached

    if not settings.OPENAI_API_KEY or OpenAIEmbeddings is None:
        # Fall back to deterministic pseudo-embedding for local/dev testing
        vector = [float(int(b, 16)) / 255.0 for b in _hash_text(text)[:32]]
        await _store_vector(text, vector)
        return vector

    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL,
    )
    vector = await embeddings.aembed_query(text)
    await _store_vector(text, vector)
    return vector
