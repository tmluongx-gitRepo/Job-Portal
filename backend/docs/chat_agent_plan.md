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
     - ✅ Returns placeholder matches for now; integration with embeddings/Chroma pending.
   - `EmployerAgent`:
     - ✅ Returns placeholder candidates; real retrieval to follow.
7. **Shared tools**
   - `chain.py`: ✅ stub LangChain v1 runnables for each agent (ready to swap with real chains).
   - `tools/retrievers.py`: wrappers around Chroma queries, embedding generation, caching, implemented with LangChain v1 retriever + runnable patterns (TBD).
   - `tools/scoring.py`: matching score calculation (e.g., weighted cosine similarity + metadata filters) (TBD).
   - `tools/prompts.py`: prompt templates for each agent (TBD).

### Phase 3 – Streaming & Caching (pending)
8. **Streaming implementation**
   - ✅ Orchestrator emits match payloads plus tokenised responses over WebSocket.
   - TODO: switch to real LangChain streaming once OpenAI integration is enabled.
9. **Caching hooks**
   - Decorate embedding/LLM calls with Redis caching (`cache_embedding`, `cache_llm_response`).
   - Cache conversation summaries keyed by `(user_id, session_id)`.
   - Detect repeated intents (e.g., same question) and short-circuit if cached response exists.

### Phase 4 – Persistence & Summaries (pending)
10. **Long-term history**
    - Save messages and agent responses to Mongo after each turn.
    - Implement periodic summarisation (post N turns) to reduce future context size.
    - Store summary checkpoints in both Mongo and Redis.
11. **Resume session**
    - On socket connect, fetch latest session summary + last few messages from Mongo, warm Redis cache, and send optional “context restored” event to frontend.

### Phase 5 – Monitoring, Testing, Docs (pending)
12. **Monitoring**
    - Integrate LangSmith (or similar) in orchestrator + agents for tracing and cost tracking.
    - Add structured logging around agent decisions and retrieval hits/misses.
13. **Testing**
    - Unit tests for session service, Redis cache, embedding caching.
    - Integration test using async WebSocket client (without hitting real OpenAI by mocking LLM responses).
    - Load test stubs to verify streaming performance and Redis eviction behaviour.
14. **Documentation**
    - Update `ARCHITECTURE.md` with new chat subsystem summary.
    - Create developer guide for running chat websocket locally and seeding test data.

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
- Exact matching score formula (cosine similarity + domain-specific weighting?)
- Fallback behaviours when Chroma or embeddings unavailable (e.g., friendly message vs direct DB search).
- Rate limiting / concurrency controls per user.
- Frontend protocol for receiving structured payloads in addition to text tokens.

---

## Hand-off Status (as of this document)

- ✅ Phase 0 scaffolding landed (configuration + module skeletons).
- ✅ Phase 1 (session persistence + Redis cache) in progress — storage layer completed.
- ✅ WebSocket streaming loop echoes structured responses per role.
- Next immediate tasks: replace stub chains with real LangChain retrieval + LLM streaming.

If you pick up this work, please update this file with progress notes and any new decisions so the next teammate has a clear starting point.
