# Development Guide

## Architecture Overview

This project uses a **single devcontainer** approach where all development happens in one container. This avoids `node_modules` sync issues between multiple containers.

## Container Setup

- **devcontainer** - Your main development environment
  - Has Bun (for frontend) and Python/UV (for backend)
  - Port 3000 exposed for frontend
  - Port 8000 exposed for backend (via separate backend container)
  - All code mounted at `/workspace`

- **backend** - Separate container for FastAPI (still needed for services)
- **chromadb** - Vector database
- **redis** - Cache

## Starting the Development Servers

### Both Frontend & Backend Auto-Start! ✅

When you run:
```bash
# From host machine
docker compose up -d
```

**Everything starts automatically:**
- ✅ Frontend (Next.js) - runs in devcontainer on port 3000
- ✅ Backend (FastAPI) - runs in backend container on port 8000
- ✅ ChromaDB, Redis - all services up

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**View Logs:**
```bash
# From host machine
docker compose logs -f devcontainer  # Frontend logs
docker compose logs -f backend       # Backend logs

# Or use Docker Desktop UI to view logs
```

**Restart if needed:**
```bash
# From host machine
docker compose restart devcontainer  # Restart frontend
docker compose restart backend       # Restart backend

# Or click "Restart" in Docker Desktop UI
```

### Manual Start (if needed)

If you stop the container and want to manually start the frontend:

```bash
# From inside devcontainer
/workspace/start-frontend.sh
```

## Package Management

### Frontend (JavaScript/TypeScript)
- ✅ Use: `bun install`, `bun add <package>`, `bun remove <package>`
- ❌ Don't use: `npm` (disabled)

### Backend (Python)
- ✅ Use: `uv pip install`, `uv pip install -r requirements.txt`
- ❌ Don't use: `pip` (disabled)

## Why This Setup?

**Problem with separate containers:**
- When frontend runs in a separate container, it has an isolated `node_modules` volume
- Installing packages in devcontainer doesn't sync to the frontend container
- This causes "Module not found" errors

**Solution:**
- Run frontend dev server FROM the devcontainer
- Both your editor and the dev server use the SAME `node_modules`
- No sync issues! 🎉

## Common Tasks

### Install a new frontend package
```bash
cd /workspace/frontend
bun add <package-name>
# Dev server will auto-reload
```

### Install a new backend package
```bash
cd /workspace/backend
# Add package to requirements.txt
uv pip install -r requirements.txt
docker compose restart backend  # from host
```

### Rebuild containers
```bash
# From host machine
docker compose up -d --build
```

## Troubleshooting

### "Module not found" in frontend
```bash
cd /workspace/frontend
bun install
# Restart your dev server
```

### TypeScript errors in editor
```bash
# In VS Code/Cursor
Cmd/Ctrl + Shift + P
> TypeScript: Restart TS Server
```

### Backend not responding
```bash
# From host machine
docker compose logs backend
docker compose restart backend
```

