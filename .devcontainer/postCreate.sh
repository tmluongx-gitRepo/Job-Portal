#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Setting up devcontainer dependencies..."

if [ -d "/workspace/frontend" ]; then
  echo "📦 Installing frontend dependencies with bun..."
  (cd /workspace/frontend && bun install)
else
  echo "⚠️  frontend directory not found; skipping bun install."
fi

if [ -d "/workspace/backend" ]; then
  echo "🐍 Installing backend dependencies with uv..."
  (
    cd /workspace/backend
    if [ -d ".venv" ]; then
      echo "   Removing existing .venv..."
      rm -rf .venv
    fi
    echo "   Creating virtual environment with python3..."
    if ! UV_LINK_MODE=copy uv venv --python python3 .venv >/dev/null 2>&1; then
      echo "   Default python interpreter failed, trying python3.11..."
      UV_LINK_MODE=copy uv venv --python python3.11 .venv
    fi
    echo "   Installing requirements.txt into .venv..."
    UV_LINK_MODE=copy uv pip install --python .venv/bin/python -r requirements.txt
  )
else
  echo "⚠️  backend directory not found; skipping uv install."
fi

echo "✅ Devcontainer setup complete. Start the stack with 'docker compose up -d'."

if command -v gh >/dev/null 2>&1; then
  cat <<'EOF'
🔐 Authenticate GitHub access:
   gh auth login --web --git-protocol ssh
   gh auth setup-git
EOF
fi

echo "🔗 Configuring git alias 'push-auth'..."
git config --global --unset alias.push >/dev/null 2>&1 || true
git config --global alias.push-auth '!bin/git-push-auth'

if ! grep -q "Job Portal git push wrapper" ~/.bashrc 2>/dev/null; then
  cat <<'EOF' >> ~/.bashrc

# Job Portal git push wrapper
if [ -f /workspace/bin/git-push-auth ]; then
  git() {
    if [ "$1" = "push" ]; then
      shift
      /workspace/bin/git-push-auth "$@"
    else
      command git "$@"
    fi
  }
fi

EOF
fi

