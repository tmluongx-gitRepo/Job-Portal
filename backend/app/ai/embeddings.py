"""Utilities for generating and caching OpenAI embeddings."""

from __future__ import annotations

import hashlib
import importlib
import json
import logging
from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Any, cast

from pydantic import SecretStr

from app.ai.chat.cache import RedisChatCache, get_chat_cache
from app.config import settings

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from langchain_openai import OpenAIEmbeddings as OpenAIEmbeddingsCallable
else:  # pragma: no cover - runtime fallback typing
    OpenAIEmbeddingsCallable = Any


def _resolve_openai_embeddings_cls() -> Any | None:
    try:
        module = importlib.import_module("langchain_openai")
    except ImportError:  # pragma: no cover - optional dependency
        return None
    factory = getattr(module, "OpenAIEmbeddings", None)
    if callable(factory):
        return factory
    return None


_OPENAI_EMBEDDINGS_CLS = _resolve_openai_embeddings_cls()


_logger = logging.getLogger(__name__)


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

    embeddings_cls = _OPENAI_EMBEDDINGS_CLS
    if not settings.OPENAI_API_KEY or embeddings_cls is None:
        if not settings.DEBUG:
            raise RuntimeError(
                "OpenAI embeddings unavailable; configure OPENAI_API_KEY before running in non-debug mode."
            )
        # Fall back to deterministic pseudo-embedding for local/dev testing only
        _logger.warning(
            "embeddings.fallback_vector_used",
            extra={"reason": "openai_disabled", "text_hash": _hash_text(text)},
        )
        vector = [float(int(b, 16)) / 255.0 for b in _hash_text(text)[:32]]
        await _store_vector(text, vector)
        return vector

    embeddings_factory = cast(OpenAIEmbeddingsCallable, embeddings_cls)
    embeddings = embeddings_factory(
        api_key=SecretStr(settings.OPENAI_API_KEY),
        model=settings.OPENAI_EMBEDDING_MODEL,
    )
    vector = await embeddings.aembed_query(text)
    await _store_vector(text, vector)
    return vector
