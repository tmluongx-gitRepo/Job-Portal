# Docker Setup Update - Important!

## What Changed

The `docker-compose.yml` file has been updated. The frontend service is now **consolidated into the devcontainer** instead of running as a separate container. This means:

- ✅ Frontend now runs inside `job-portal-dev` container (port 3000)
- ❌ The separate `job-portal-frontend` container has been removed

## If You're Getting Errors

If you're seeing errors like:
- "Found orphan containers" warnings
- "Port is already allocated" errors
- Frontend container missing or not connecting

**This is normal after pulling the latest changes!** Your old containers are still running and need to be cleaned up.

## Quick Fix

Run these commands to clean everything up and start fresh:

```bash
# Stop all containers
docker compose down

# If you still see orphaned containers, remove them manually:
docker stop job-portal-frontend  # (or any orphaned container name)
docker rm job-portal-frontend

# Start everything fresh with orphan cleanup
docker compose up --remove-orphans
```

The `--remove-orphans` flag will automatically clean up any containers that are no longer defined in the compose file.

## Verify It's Working

After starting, you should see:
- `job-portal-dev` running on port 3000 (frontend)
- `job-portal-backend` running on port 8000
- `job-portal-chromadb` running on port 8001
- `job-portal-redis` running on port 6379

Check with: `docker compose ps`

## Need Help?

If you're still having issues, try:
```bash
# Nuclear option - stop everything
docker compose down
docker stop $(docker ps -aq)  # Stop all containers
docker compose up --remove-orphans
```

---

**Note:** This change was made to avoid node_modules sync issues between containers. The frontend now runs directly from the devcontainer, which provides better development experience.

