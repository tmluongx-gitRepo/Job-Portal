# Conversational Agent & Streaming Chat Plan

This plan documents the architecture and implementation steps for adding role-aware, streaming conversational agents to the Job Portal backend. It is intended to be a living hand-off document so any teammate can resume work knowing what has been decided, what has been delivered, and what remains open. All LangChain references assume **LangChain v1** APIs (Runnable graph, AgentExecutor, etc.) per the latest documentation.

---

## Current Context

- Backend stack: FastAPI + Motor (MongoDB) + Redis + ChromaDB + Supabase Auth (see `backend/ARCHITECTURE.md`).
- RAG resume parsing pipeline is being designed; embeddings and parsed resume data will live in Mongo + Chroma.
- Requirement: a single chat entry point that supports both job seekers and employers, streaming responses to the frontend chat box.
- Agents: Orchestrator agent (LangChain) delegates to role-specific sub-agents that use our data stores to produce contextual answers (e.g., job matches for seekers, candidate matches for employers).

---

## Guiding Principles

1. **Reuse existing infrastructure**: FastAPI routers + auth deps, Redis, ChromaDB, Mongo.
2. **Streaming-first**: Chat endpoint must support token streaming (WebSocket or Server-Sent Events) from the LLM.
3. **Role-specific intelligence**: Orchestrator decides which sub-agent to invoke based on the authenticated user (`job_seeker` vs `employer`).
4. **Cost efficiency**: Prefer OpenAI `text-embedding-3-large` with Redis caching; reuse context summaries to reduce token usage.
5. **Persistence**: Store conversation history in Mongo so context survives logouts; Redis keeps the hot cache.
6. **Traceability**: Integrate monitoring (e.g., LangSmith) for debugging chains and tracking spend.

---

## High-Level Architecture

```
Frontend Chat ↔ FastAPI streaming endpoint
                         ↓
             Authentication (Supabase JWT)
                         ↓
             Conversation Session Manager
                         ↓
                Orchestrator Agent (LangChain)
                 /                     \
        JobSeekerAgent           EmployerAgent
             ↓                         ↓
   Resume vectors + jobs        Job/employer context + candidates
    (Chroma + Mongo)             (Chroma + Mongo)
             ↓                         ↓
        LLM Response (stream via Redis caching + OpenAI)
             ↓
 Conversation log persisted (Mongo) + cached (Redis)
```

Key modules to add under `app/`:

- `app/ai/chat/` (new package)
  - `orchestrator.py`
  - `agents/job_seeker.py`, `agents/employer.py`
  - `tools/retrievers.py`, `tools/scoring.py`
  - `sessions.py` (conversation management)
- `app/api/routes/chat.py` (new router for streaming endpoint)
- `app/services/chat_history.py` (Mongo persistence helpers)
- Update `app/config.py` for new settings (LLM keys, Redis TTLs, streaming toggles)

---

## Step-by-Step Plan

### Phase 0 – Foundations (not yet started)
1. **Configuration & secrets**
   - Add OpenAI settings for `text-embedding-3-large` and chat completion model (e.g., `gpt-4o-mini` for streaming) to `app/config.py`.
   - Extend Redis settings with dedicated namespaces/TTL for chat sessions and cached embeddings/LLM outputs.
2. **Directories & packages**
   - Create `app/ai/chat/` scaffold with `__init__.py` files.
   - Decide on streaming transport (FastAPI WebSocket vs SSE); initial plan is WebSocket for bi-directional control.

### Phase 1 – Conversation Infrastructure (pending)
3. **Session persistence**
   - ✅ Mongo collections: `chat_sessions`, `chat_messages` with indexes on `user_id`, `session_id`, timestamps.
   - ✅ `ChatHistoryService` implemented with Mongo CRUD hooks.
   - ✅ Redis chat cache wrapper (`RedisChatCache`) stores summaries + recent turns with TTL.
4. **Authentication integration**
   - ✅ `/api/chat/ws` WebSocket skeleton with `get_current_user` auth guard.
   - Streaming logic to be implemented in next phase (currently returns handshake message).

### Phase 2 – Agent Orchestration (pending)
5. **Orchestrator**
   - ✅ Stub orchestrator dispatches by role and persists chat turns.
   - Next: swap stub with LangChain v1 runnable graph (streaming per token).
6. **Sub-agents**
   - `JobSeekerAgent`:
     - ✅ Streams matches with scoring breakdowns; will enrich further once real embeddings are populated.
   - `EmployerAgent`:
     - ✅ Returns re-ranked candidate shortlists with the same scoring signals; awaits live data wiring.
7. **Shared tools**
   - `chain.py`: ✅ LangChain v1 runnables with streaming/fallback support.
   - `tools/retrievers.py`: ✅ Chroma query attempt + fallback; now re-ranks results via metadata-aware scoring and surfaces component breakdowns for the UI.
   - `tools/scoring.py`: ✅ Vector/metadata fusion logic (skills/location/industry/experience) with per-component transparency.
   - `utils.py`: ✅ Match normalisation + summary helpers keep downstream prompts/events consistent.
   - `tools/prompts.py`: prompt templates for each agent (TBD).

### Phase 3 – Streaming & Caching (pending)
8. **Streaming implementation**
   - ✅ Orchestrator emits match payloads and tokenised responses via LangChain (fallback if OpenAI unavailable).
   - TODO: enable true OpenAI streaming once credentials/config available in environment.
9. **Caching hooks**
   - Decorate embedding/LLM calls with Redis caching (`cache_embedding`, `cache_llm_response`).
   - Cache conversation summaries keyed by `(user_id, session_id)`.
   - Detect repeated intents (e.g., same question) and short-circuit if cached response exists.

### Phase 4 – Persistence & Summaries (pending)
10. **Long-term history**
    - ✅ Messages persist to Mongo after each turn via `ChatHistoryService`.
    - ✅ Rolling summary updated after assistant replies (LangChain fallback when OpenAI unavailable).
    - ✅ Summary cached in Redis for fast reuse across reconnects.
11. **Resume session**
    - ✅ WebSocket hydrates summary + recent messages from cache/DB and emits them on connect.

### Phase 5 – Monitoring, Testing, Docs (pending)
12. **Monitoring**
    - ✅ LangSmith tracing toggle + context manager wired through `instrumentation.py` and invoked in stream factories.
    - ✅ Structured logging emitted from retrievers/orchestrator for match sourcing, fallbacks, and session events.
13. **Testing**
    - ✅ Unit tests for session service, Redis cache eviction, embedding caching, and match normalisation.
    - ✅ WebSocket integration test using dependency overrides to mock LangChain + persistence.
    - ✅ Cache eviction test doubles as lightweight load/retention verification.
14. **Documentation**
    - ✅ `ARCHITECTURE.md` reflects match normalisation, tracing, and structured logging.
    - ✅ `docs/chat_websocket_guide.md` documents local websocket setup + seeding expectations.

---

## Data Model Sketches (proposed)

**Mongo – `chat_sessions`**
```
{
  _id: ObjectId,
  user_id: ObjectId,
  role: "job_seeker" | "employer",
  session_id: UUID,
  status: "active" | "ended",
  last_interaction_at: datetime,
  summary: str | null,           # rolling summary for quick load
  created_at: datetime,
  updated_at: datetime
}
```

**Mongo – `chat_messages`**
```
{
  _id: ObjectId,
  session_id: UUID,
  role: "user" | "assistant",
  payload_type: "text" | "jobs" | "candidates" | ...,
  text: str,
  structured: dict | null,       # e.g., list of jobs with scores
  tokens_used: int | null,
  created_at: datetime
}
```

**Redis Keys (examples)**
```
chat:session:{session_id}:recent     # list of last N serialized messages (JSON)
chat:session:{session_id}:summary    # cached summary string
embedding:{hash}                     # cached embedding vector
llm_response:{hash}                  # cached LLM output for identical prompt/context
```

---

## Reference Links

- LangChain v1 Runnable Interfaces: https://python.langchain.com/docs/expression_language/
- LangChain v1 Agents & AgentExecutor: https://python.langchain.com/docs/modules/agents/
- LangChain v1 Streaming APIs: https://python.langchain.com/docs/expression_language/streaming

---

## Open Questions / TBD

- Final choice of streaming transport (WebSocket vs SSE) – leaning WebSocket for duplex control.
- Matching score weighting is in place; revisit the ratios once real embeddings + product feedback arrive.
- Fallback behaviours when Chroma or embeddings unavailable (e.g., friendly message vs direct DB search).
- Rate limiting / concurrency controls per user.
- Frontend protocol for receiving structured payloads in addition to text tokens.

---

## Hand-off Status (as of this document)

- ✅ Phase 0 scaffolding landed (configuration + module skeletons).
- ✅ Phase 1 (session persistence + Redis cache) in progress — storage layer completed.
- ✅ WebSocket streaming loop echoes structured responses per role.
- ✅ Rolling summaries persisted + cached after every assistant reply.
- ✅ Metadata-aware scoring + re-ranking landed (retrievers now emit score breakdowns for jobs/candidates).
- Next immediate tasks: populate Chroma with production embeddings, enable true OpenAI streaming, and lock the frontend contract for scoring payloads & event ordering.

### Upcoming Milestones
1. Populate Chroma with real resume/job embeddings so the new scoring layer has production vectors to work with.
2. Enable OpenAI streaming end-to-end (when credentials available) and add retry/backoff handling.
3. Define frontend message protocol (event types, payload schema) and document in README/architecture (in progress, see event schema above).

### Embedding Ingestion TODO
- Create embedding generation pipeline (resume + job documents) with batch processing and Chroma upsert utilities. **(In progress: see `app/ai/embeddings.py`, `app/ai/indexers.py`, `app/tasks/embedding_tasks.py`)**
- Store denormalised metadata alongside embeddings (skills, location, industry) for scoring helper to consume.
- Establish consistency checkers / backfill scripts so new resumés/jobs trigger embedding updates automatically.
- ✅ Score fusion logic (vector similarity + metadata weighting) now lives in `tools/scoring.py` and is consumed by the retrievers.

## WebSocket Event Schema

The `/api/chat/ws` endpoint streams JSON payloads with the following shapes:

| Event `type` | Payload | Notes |
|--------------|---------|-------|
| `info` | `{ "message": str, "session_id": str }` | Sent immediately after connection opens |
| `history` | `{ "messages": [ {"role": str, "payload_type": str, "text": str | null, "structured": object | null, "created_at": str } ] }` | Cached transcript (most recent messages) |
| `summary` | `{ "summary": str }` | Rolling conversation summary (updated after each assistant reply) |
| `matches` | `{ "matches": [ { "id": str, "label": str, "subtitle": str | null, "match_score": float, "vector_score": float | null, "score_breakdown": {...}, "reasons": [str], "source": str, "metadata": {...} } ], "summary": str }` | Structured match list (sorted by `match_score`) plus a human-readable summary |
| `token` | `{ "text": str }` | Streaming token/text chunk (LangChain/OpenAI when enabled) |
| `complete` | `{}` | Signals end of assistant turn |
| `error` | `{ "message": str }` | Reserved for failure cases |

Clients should handle receiving `history` and `summary` immediately after the initial `info`, then append `token` chunks until a `complete` event arrives. `matches` can appear before tokens when relevant. Future enhancements may add `metadata` fields (e.g., scoring breakdowns) but will remain backward-compatible.

If you pick up this work, please update this file with progress notes and any new decisions so the next teammate has a clear starting point.
