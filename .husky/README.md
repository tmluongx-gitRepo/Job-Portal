# Git Hooks with Husky

This directory contains Git hooks managed by [Husky](https://typicode.github.io/husky/) to maintain code quality and enforce development workflows for the Job Portal project.

## Overview

We use a **two-stage gate approach** to catch issues early:

1. **Pre-commit** - Fast checks on staged files (linting, formatting, type-checking)
2. **Pre-push** - Comprehensive validation before code sharing (builds, tests, full checks)

## Hooks

### 🔍 Pre-Commit Hook

Runs **fast checks** on staged files before allowing a commit:

**Always runs:**
- `lint-staged` - Auto-formats and lints only the files you're committing

**Conditional checks** (only if files in that directory are staged):

| Directory | Checks Performed |
|-----------|------------------|
| `frontend/` | ✅ ESLint linting<br>✅ TypeScript type checking |
| `backend/` | ✅ Ruff linting<br>✅ Ruff format checking |

**Purpose:** Catch syntax errors, type issues, and formatting problems immediately while they're fresh in your mind.

---

### 🚀 Pre-Push Hook

Runs **comprehensive validation** before pushing to remote:

**Git Workflow Protection:**
- 🚫 Blocks direct pushes to `main` branch (requires feature branches + PRs)
- 🔒 Prevents `.env` files from being tracked in version control

**Conditional validation** (only runs for changed code):

| Directory | Validation Performed |
|-----------|---------------------|
| `frontend/` | ✅ Full ESLint check<br>✅ TypeScript type checking<br>✅ Production build test<br>⚠️ Tests (when configured) |
| `backend/` | ✅ Full Ruff linting<br>✅ Ruff format checking<br>⚠️ pytest suite (warning only if failing) |

**Purpose:** Ensure your code builds correctly and passes all quality checks before sharing with the team.

---

## Setup

### Automatic Setup (Recommended)

Husky hooks are **automatically installed** when you run:

```bash
cd frontend
bun install
```

The `prepare` script in `package.json` configures Husky for you.

### Manual Setup

If automatic setup doesn't work:

```bash
# From the project root
cd frontend
npx husky install ../.husky
```

---

## Bypassing Hooks

### When to bypass

You might need to bypass hooks when:
- Making a quick fix during an emergency
- Working with known issues that will be fixed later
- Debugging git hook problems

### How to bypass

**Skip pre-commit:**
```bash
git commit --no-verify -m "your message"
# or shorthand
git commit -n -m "your message"
```

**Skip pre-push:**
```bash
git push --no-verify
# or shorthand
git push -n
```

### ⚠️ Important Warning

While you can bypass hooks locally, **CI/CD will still enforce all checks**. Bypassing hooks locally will likely result in failed builds in CI/CD, so use this sparingly!

---

## Technology Stack

This project uses:

**Frontend:**
- Next.js 15 + React 19 + TypeScript
- Bun (package manager)
- ESLint + Prettier (linting/formatting)

**Backend:**
- FastAPI + Python 3.12
- uv (package manager)
- Ruff (linting/formatting)
- pytest (testing)

**Infrastructure:**
- Docker Compose (MongoDB, ChromaDB, Redis)
- Husky (Git hooks)
- lint-staged (Staged file processing)

---

## Troubleshooting

### "Husky command not found"

**Solution:** Install dependencies first:
```bash
cd frontend
bun install
```

### "Permission denied" when running hooks

**Solution:** Make hooks executable:
```bash
chmod +x .husky/pre-commit .husky/pre-push
```

### "frontend/ directory not found" warning

This can happen in Git worktrees or if you're running hooks from an unusual location. The hooks will gracefully skip checks for missing directories with a warning.

### Pre-push fails on "main" branch

This is **intentional** - direct pushes to `main` are blocked to enforce a PR workflow.

**Solution:**
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Push to your feature branch: `git push -u origin feature/your-feature-name`
3. Open a Pull Request on GitHub

### Backend tests failing but you need to push

The pre-push hook treats backend test failures as **warnings only** during development. You'll see the failure but the push will continue. However, you should fix tests before merging to `main`.

---

## Hook Configuration Files

| File | Purpose |
|------|---------|
| `.husky/pre-commit` | Pre-commit hook script |
| `.husky/pre-push` | Pre-push hook script |
| `frontend/package.json` | Contains `lint-staged` config and `prepare` script |
| `backend/ruff.toml` | Ruff linting configuration |
| `frontend/.eslintrc.json` | ESLint configuration |
| `frontend/tsconfig.json` | TypeScript configuration |

---

## Development Workflow

### Recommended Git Flow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/add-user-auth
   ```

2. **Make changes and commit** (pre-commit hook runs):
   ```bash
   git add .
   git commit -m "feat: add user authentication"
   # → Runs lint-staged, ESLint, TypeScript, Ruff
   ```

3. **Push to remote** (pre-push hook runs):
   ```bash
   git push -u origin feature/add-user-auth
   # → Runs full validation, builds, tests
   ```

4. **Create Pull Request** on GitHub

5. **Merge after approval** (never push directly to `main`)

---

## Adding New Hooks

To add a new Git hook:

```bash
# Create the hook file
echo '#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "Running my custom hook..."
# Your commands here
' > .husky/hook-name

# Make it executable
chmod +x .husky/hook-name
```

Common hooks:
- `commit-msg` - Validate commit message format
- `post-commit` - Run actions after commit
- `post-checkout` - Run actions after branch checkout

---

## Resources

- [Husky Documentation](https://typicode.github.io/husky/)
- [lint-staged Documentation](https://github.com/okonet/lint-staged)
- [Conventional Commits](https://www.conventionalcommits.org/) (recommended commit format)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

## Questions?

If you encounter issues with Git hooks, check:
1. Are dependencies installed? (`cd frontend && bun install`)
2. Are hooks executable? (`ls -la .husky/pre-*`)
3. Is Husky initialized? (Look for `.husky/_/husky.sh`)

For persistent issues, contact the development team or open an issue on GitHub.
