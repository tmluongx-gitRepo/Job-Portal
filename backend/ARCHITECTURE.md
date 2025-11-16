# Job Portal Backend Architecture

This document captures the current architecture of the Job Portal backend so new contributors can understand how requests travel through the system, what services and data stores we depend on, and where to extend functionality.

---

## High-Level Overview

- **Framework:** Async [FastAPI](https://fastapi.tiangolo.com/) application served by Uvicorn with full type hints and Pydantic v2 validation.
- **Primary data store:** MongoDB accessed through the Motor async driver. Collections are described with `TypedDict` definitions in `app/type_definitions.py` so CRUD helpers can return strongly-typed documents.
- **Authentication:** Supabase Auth owns user credentials and access/refresh tokens. The backend validates Supabase JWTs with `SUPABASE_JWT_SECRET`, performs just-in-time (JIT) provisioning of Mongo user records, and adds RBAC helpers to every protected route.
- **Caching / coordination:** Redis is provisioned and pinged on startup. It is currently used for health checking but can be promoted to caching or queueing without code changes.
- **Vector search preparation:** ChromaDB is initialised at startup so recommendation work can move to vector search. For now, recommendation endpoints operate entirely on Mongo data.
- **File storage:** Dropbox holds Job Seeker resumes. Uploads replace `/resumes/{user_id}.pdf`, and downloads stream content back to clients.
- **Automation:** n8n integration is supported via outbound webhooks (see `backend/app/services/webhook_service.py`). Local Docker provisioning has been removed; point `N8N_WEBHOOK_URL` at your managed n8n instance if needed.
- **Domain scope:** REST APIs cover authentication, user management, job seeker and employer profiles, job postings, applications, interviews, saved jobs, resumes, recommendations, and analytics/insights across those resources.

Typical call stack:

```
FastAPI router  →  auth dependency / service  →  CRUD module  →  Motor client (Mongo)
```

---

## Source Layout

```
app/
├── main.py                 # FastAPI app creation & lifespan hook
├── config.py               # Environment settings via pydantic-settings
├── database.py             # Mongo/Redis/Chroma clients + index initialisation
├── type_definitions.py     # TypedDicts for Mongo collections
├── constants.py            # Shared enums (application/interview status)
├── auth/                   # Supabase integration, JWT utilities, dependencies, routes
├── api/routes/             # Domain routers grouped by resource
├── crud/                   # Async data-access helpers for each collection
├── schemas/                # Pydantic request/response contracts
├── utils/                  # Dropbox + datetime helpers
└── models/                 # ChromaDB document helpers (not yet wired into API)

tests/
├── conftest.py             # Async fixtures, Supabase test account enable/ban lifecycle
├── fixtures/test_users.py  # Persistent Supabase test account definitions
├── auth/                   # RBAC coverage per resource
├── endpoints/, integration/ # Workflow and end-to-end scenarios
└── test_*                  # Security (JWT), analytics, and workflow suites
```

---

## Request and Data Flow

1. **Routers (`app/api/routes/…`)** expose HTTP endpoints grouped by domain. Every route loads Pydantic request models, returns Pydantic response models, and immediately applies role-aware dependencies.
2. **Auth dependencies (`app/auth/dependencies.py`)** decode Supabase JWTs, enforce role requirements (`require_job_seeker`, `require_employer`, `require_admin`), and trigger JIT Mongo provisioning through `app/auth/user_service.py`.
3. **Service layer:** the only dedicated service today is `user_service`, whose job is to bridge Supabase IDs to Mongo ObjectIds. Other routes call CRUD helpers directly after dependency checks.
4. **CRUD helpers (`app/crud/*.py`)** encapsulate Mongo access, collection-specific indexes, and side-effects (e.g., cancelling interviews when an application is accepted). They return the `TypedDict` structures defined in `type_definitions.py`.
5. **Response serialization** happens in the router functions, which convert Mongo documents into response schemas and embed related details (e.g., job details on recommendations, resume metadata on profiles).

### Domain Notes
- **Authentication (`app/auth/routes.py`):** wraps Supabase sign-up/in/out/refresh flows, forces Supabase calls onto worker threads, and surfaces consistent HTTP error handling.
- **Users (`app/api/routes/users.py`):** admin-only management plus self-service endpoints. Uses `user_service` to ensure operations are performed on Mongo IDs.
- **Profiles & Jobs:** job seeker and employer routers enforce ownership, hydrate resumes or job stats, and lean on CRUD functions for collection filtering and aggregation.
- **Applications & Interviews:** application endpoints coordinate status transitions, enforce business rules (terminal states, duplicate prevention), and trigger cascading side-effects (mark job filled, cancel interviews). Interview endpoints add role-based field filtering when serialising responses.
- **Recommendations, Saved Jobs, Resumes:** each router layers additional services (Dropbox, enrichment lookups) on top of Mongo documents.

---

## Startup & Lifespan (`app/main.py`)

The FastAPI app defines an async `lifespan` context manager:

1. **Log startup banner** including app name/version from configuration.
2. **ChromaDB:** create a reusable HTTP client, log heartbeat success or a warning on failure.
3. **MongoDB:** enforce that `MONGO_URI` is not left at the placeholder and ping the database. After connection succeeds, `init_db_indexes()` creates/ensures indexes across all collections (users, job seeker profiles, employer profiles, jobs, applications, recommendations, saved jobs, resumes, interviews).
4. **Redis:** attempt a ping and log basic server info; errors downgrade startup to a warning.
5. **Supabase:** lazily import the global client and report whether authentication is configured.
6. **Shutdown:** log a shutdown message and close the cached Mongo client.

Routers are then registered with CORS enabled via settings (`settings.CORS_ORIGINS`).

---

## Persistence & External Integrations

### MongoDB
- Accessed through Motor with the global client created on demand (`get_mongo_client`). Atlas SRV URIs automatically enable TLS.
- Collections mirror the domain (users, job_seeker_profiles, employer_profiles, jobs, applications, recommendations, saved_jobs, resumes, interviews).
- Indexes include unique constraints (e.g., one profile per user, one application per profile/job pair) and compound indexes for filters and analytics.
- Type-safe `TypedDict` definitions keep CRUD helpers and routers aligned on document structure.

### Supabase Auth
- `app/auth/supabase_client.py` attempts to instantiate a global Supabase client using anon credentials; missing configuration downgrades to warnings so local development can still run.
- JWTs are decoded with PyJWT and the Supabase secret, enforcing signature validation, `aud="authenticated"`, and expiration. Invalid tokens raise domain-specific exceptions which map to `401` responses.
- JIT provisioning constrains self-assigned roles to `job_seeker` or `employer`; higher privilege roles must be assigned by an admin inside MongoDB.

### Redis
- Configured by URL (`settings.REDIS_URL`) and only used for health checks today (`/health`). The async Redis client is closed immediately after pinging to avoid leaked connections.

### ChromaDB
- `get_chroma_client()` builds an HTTP client with telemetry disabled. `get_collection()` is available for future vector search work but the current recommendation endpoints rely solely on Mongo data enrichment.
- `app/models/job.py` and `app/models/user.py` define helper classes for shaping documents/metadata should Chroma integration expand.

### Dropbox
- `DropboxService` wraps uploads, downloads, and deletes with helpful error messages. Uploads overwrite the single stored resume per job seeker and store metadata in Mongo. Missing credentials raise explicit configuration errors.

### Docker Compose Footprint
- `backend` service runs the FastAPI app with live reload.
- `chromadb` and `redis` are provisioned for local development.
- `devcontainer` is the recommended way to run the Next.js frontend alongside the backend.
- **MongoDB is deliberately excluded**; provide `MONGO_URI` pointing to an Atlas cluster or local instance.

---

## API Surface Summary

| Router | Path Prefix | Purpose |
|--------|-------------|---------|
| `health` | `/health` | Service + dependency health check (Mongo/Redis) |
| `auth` | `/api/auth` | Supabase-backed register/login/logout/refresh/password flows |
| `users` | `/api/users` | Admin user management, self-service update/delete, lookup helpers |
| `job_seeker_profiles` | `/api/job-seeker-profiles` | CRUD plus analytics for job seekers, resume links |
| `employer_profiles` | `/api/employer-profiles` | Company profiles and employer analytics |
| `jobs` | `/api/jobs` | CRUD, search, analytics for job postings |
| `applications` | `/api/applications` | Apply, list, status transitions with cascading effects |
| `interviews` | `/api/interviews` | Schedule/reschedule/cancel/complete interviews with role-aware responses |
| `saved_jobs` | `/api/saved-jobs` | Save, list, and remove bookmarked jobs |
| `resumes` | `/api/resumes` | Upload metadata + Dropbox-backed download/delete flow |
| `recommendations` | `/api/recommendations` | CRUD plus enriched responses for AI-driven job matches |

Every router imports shared auth dependencies to enforce RBAC consistently.

### Conversational Chat (LangChain scaffolding)
- **Endpoint:** `/api/chat/ws` (FastAPI WebSocket) authenticates via Supabase JWT and streams JSON events (`info`, `history`, `summary`, `matches`, `token`, `complete`, `error`). See `docs/chat_agent_plan.md` for the event schema.
- **Session handling:** `ChatSessionStore` + `ChatHistoryService` persist transcripts in Mongo (`chat_sessions`, `chat_messages`) and cache summaries/recent turns in Redis to warm reconnects.
- **Orchestrator:** `ChatOrchestrator` selects job-seeker vs employer agent, streams LangChain output (fallback tokens if OpenAI unavailable), emits normalised match payloads with score breakdowns + summaries, persists them as `payload_type="matches"`, and refreshes a rolling conversation summary.
- **Agents & tools:** `app/ai/chat/agents/*` call runnables defined in `app/ai/chat/chain.py`; `tools/retrievers.py` now re-ranks vector results (or metadata fallbacks) using `tools/scoring.py`, feeding structured reasons into the prompt formatter so downstream consumers see why an item scored well.
- **Embedding pipeline:** `app/ai/embeddings.py`, `app/ai/indexers.py`, `app/tasks/embedding_tasks.py` provide scaffolding for generating embeddings and upserting them into Chroma (jobs/resumes).
- **Monitoring:** `app/ai/chat/instrumentation.py` toggles LangSmith tracing via settings and exposes the `logger` used across retrievers/orchestrator for structured event logs.

---

## Testing & Quality Gates

- **Pytest configuration:** defined in `pyproject.toml` (`asyncio_mode = auto`). Test suite is fully async-aware.
- **Fixtures (`tests/conftest.py`):** manage Supabase test accounts (auto enable before session, ban after), provide HTTP clients, and ensure each test runs against the `MONGO_TEST_DB_NAME` database.
- **RBAC tests (`tests/auth/test_*`):** ensure only authorised roles can hit each endpoint.
- **Workflow tests:** cover acceptance workflows (job posted → application → interview → status transitions) and analytics endpoints.
- **Security tests:** `tests/test_jwt_verification.py` verifies signature enforcement, expiry checks, and audience validation for Supabase JWTs.
- **Static analysis:** Ruff and MyPy run with strict settings; all application modules are fully typed.

---

## Operational Considerations & Gaps

- **Logging:** startup uses `print` statements with emoji prefixes for visibility. Production deployments should replace this with structured logging and centralised monitoring.
- **Redis & Chroma:** currently health-checked only. Future work can add caching layers, background jobs, or vector search leveraging the existing wiring.
- **Mongo provisioning:** ensure developers configure a real `MONGO_URI`; leaving the placeholder raises a `ConnectionError` during startup.
- **File handling:** Dropbox operations do not currently retry or stream uploads asynchronously. Consider backoff/retry or background processing for large files.
- **Observability:** metrics and tracing are not yet instrumented. OpenTelemetry or similar tooling can be added without disrupting current structure.
- **Docs vs reality:** the repository `backend/README.md` still references SQLAlchemy/PostgreSQL from an earlier scaffold. This architecture document reflects the actual Mongo/Supabase-driven implementation.

---

## Quick Reference

- **Run locally:** `uvicorn app.main:app --reload`
- **Auth dependency import:** `from app.auth.dependencies import get_current_user`
- **Mongo database handle:** `from app.database import get_mongo_database`
- **Resume storage helper:** `from app.utils.dropbox_utils import get_dropbox_service`
- **Environment file:** `.env` at repository root (`Job-Portal/.env`) controls all runtime configuration.

This document should be the starting point for future design discussions, including the planned agent integrations.
