# Chat WebSocket Developer Guide

This guide documents how to run the role-aware chat websocket locally, seed data for smoke testing, and observe the monitoring signals added in Phase 5.

## Prerequisites

- Backend dependencies installed (`poetry install` or `pip install -r requirements.txt`).
- Local services running: MongoDB, Redis, ChromaDB (use `docker-compose up backend-deps` if available).
- `.env` populated with local connection strings and an OpenAI key if you want live streaming (otherwise the fallback stubs will be used).
- Supabase credentials set only if you intend to hit authenticated HTTP routes; the websocket test plan below relies on dependency overrides so it can run without Supabase.

## Running the WebSocket Locally

1. Launch the backend API:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. From the repo root, connect to the websocket using the provided example client:

   ```bash
   python scripts/dev_ws_client.py --token <supabase-jwt> --message "Show me suitable roles"
   ```

   The initial events should include `info`, `summary`, and `history`, followed by structured `matches` and token streams.

3. To simulate employer vs job seeker flows locally, adjust the Supabase JWT (or temporarily patch `get_current_user` in `app/api/routes/chat.py`).

## Seeding Data for Local Chat

- **Mongo**: insert representative job seeker profiles, employer profiles, jobs, applications, and chats using the `tests/fixtures` JSON payloads as templates.
- **Chroma**: run the ingestion helpers in `app/tasks/embedding_tasks.py` or call `upsert_job_embedding` / `upsert_candidate_embedding` directly after your seed inserts.
- **Redis**: no manual seeding is required; the chat orchestrator writes recent messages and summaries automatically.

For quick smoke tests without full seed data, rely on the metadata fallbacks baked into `tools/retrievers.py`—they return deterministic sample matches.

## Monitoring & Observability

- Structured logs are emitted under the `app.ai.chat` namespace. Configure Python logging (e.g., via `LOGURU_LEVEL=INFO` or adding a basicConfig block) to surface events such as `chat.matches_emitted` and `chat.retriever.vector_results`.
- Enable LangSmith tracing by setting `LANGCHAIN_TRACING_ENABLED=true` and `LANGCHAIN_PROJECT=<project-name>` in your `.env`. The orchestrator automatically configures environment variables and wraps streaming calls in tracing contexts.
- The monitoring test suite exercises these flows without external services:

  ```bash
  cd backend
  pytest tests/test_chat_cache_eviction.py tests/test_chat_match_utils.py tests/test_chat_session_store.py tests/test_chat_websocket.py
  ```

## Development Tips

- When iterating on the websocket, use the dependency overrides in `tests/test_chat_websocket.py` as a reference for mocking persistence and LLMs.
- Keep an eye on Redis TTLs (default 48h). Adjust `CHAT_SESSION_TTL_SECONDS` in `config.py` if you need shorter-lived caches during development.
- Update `docs/chat_agent_plan.md` with any new protocol changes so the next teammate has a clear hand-off.
