# Job Portal

A full-stack job portal application built with Next.js and FastAPI, fully containerized with Docker.

## Tech Stack

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS

**Backend:**
- FastAPI
- Python 3.12
- ChromaDB (Vector Database)
- Redis

## Prerequisites

Before you start, you need to install:

1. **Docker Desktop** - Download from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Choose your operating system (Mac, Windows, or Linux)
   - Install and launch Docker Desktop
   - Make sure Docker Desktop is running (you'll see a whale icon in your system tray)

2. **Cursor IDE** (or VSCode) - Download from [https://cursor.sh](https://cursor.sh)
   - Install Cursor
   - Launch Cursor to make sure it works

**That's it!** No need to install Node, Python, ChromaDB, or Redis locally. Docker handles everything!

---

## 🚀 Complete Setup Guide (For Beginners)

Follow these steps exactly as written. Don't skip any steps!

### Step 1: Install Docker Desktop

1. Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Download Docker Desktop for your operating system
3. Install it (follow the installer instructions)
4. **Launch Docker Desktop** and wait for it to start
5. Verify Docker is running:
   - **Mac/Linux**: Open Terminal and run: `docker --version`
   - **Windows**: Open PowerShell or Command Prompt and run: `docker --version`
   - You should see something like: `Docker version 24.0.0, build abc1234`

**✅ Success Check:** Docker Desktop is running and you can see the whale icon in your menu bar (Mac) or system tray (Windows)

---

### Step 2: Install Cursor IDE

1. Go to [https://cursor.sh](https://cursor.sh)
2. Download Cursor for your operating system
3. Install it
4. Launch Cursor to make sure it opens

**✅ Success Check:** Cursor opens and you see the welcome screen

---

### Step 3: Clone the Repository

Open your **Terminal** (Mac/Linux) or **Command Prompt/PowerShell** (Windows):

```bash
# Navigate to where you want to store the project
# For example, your Documents folder:
cd ~/Documents  # Mac/Linux
cd %USERPROFILE%\Documents  # Windows

# Clone the repository
git clone <YOUR-REPO-URL-HERE>

# Enter the project folder
cd Job-Portal
```

**Replace `<YOUR-REPO-URL-HERE>`** with the actual GitHub repository URL (ask your team lead for this!)

**✅ Success Check:** You're now inside the `Job-Portal` folder. Run `ls` (Mac/Linux) or `dir` (Windows) and you should see folders like `frontend`, `backend`, `.devcontainer`, etc.

---

### Step 4: Create Environment File

Still in your terminal, inside the `Job-Portal` folder:

```bash
# Mac/Linux:
cp .env.example .env

# Windows (PowerShell):
Copy-Item .env.example .env

# Windows (Command Prompt):
copy .env.example .env
```

**✅ Success Check:** You now have a `.env` file in your project folder (you can verify with `ls -la` on Mac/Linux or `dir` on Windows)

---

### Step 5: Build and Start Docker Containers

**IMPORTANT:** Make sure Docker Desktop is running before this step!

In your terminal (still inside the `Job-Portal` folder):

```bash
docker compose up
```

**What this does (First Time):**
- Downloads all necessary Docker images (Node, Python, ChromaDB, Redis)
- **Automatically builds** your frontend and backend containers
- Installs all dependencies (npm packages, Python packages)
- Starts ChromaDB vector database
- Starts Redis cache
- Starts all services
- **Takes 5-10 minutes** (be patient!)

**You'll see lots of logs scrolling. That's normal!** Wait until you see messages like:
```
job-portal-frontend  | Ready in 2.1s
job-portal-backend   | Uvicorn running on http://0.0.0.0:8000
```

**✅ Success Check:**
- Open browser and go to **http://localhost:3000** - You should see the Job Portal homepage
- Open browser and go to **http://localhost:8000/docs** - You should see the FastAPI documentation

**Keep this terminal window open!** Docker needs to keep running. Open a **new terminal** for the next steps.

**Next Time:** When you run `docker compose up` again, it will be much faster (10-30 seconds) because everything is already built!

---

### Step 6: Open Project in Cursor

Open a **new terminal window/tab**, then:

```bash
# Navigate to the project (if not already there)
cd ~/Documents/Job-Portal  # Adjust path as needed

# Open Cursor in this folder
cursor .
```

If `cursor .` doesn't work, you can:
- Open Cursor manually
- Go to **File → Open Folder**
- Select the `Job-Portal` folder

**✅ Success Check:** Cursor opens with your Job-Portal project loaded in the sidebar

---

### Step 7: Install Dev Containers Extension in Cursor

This is **THE MOST IMPORTANT STEP** for getting full IDE support!

1. **Open Extensions Panel:**
   - Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows)
   - OR click the Extensions icon in the left sidebar (looks like 4 squares)

2. **Search for Dev Containers:**
   - Type `Dev Containers` in the search box at the top

3. **Install the Extension:**
   - Look for **"Dev Containers"** by **Anysphere** (should be the first result)
   - Click the **"Install"** button
   - Wait for it to install (should take a few seconds)

**✅ Success Check:** The extension shows "Installed" and you see a green checkmark

---

### Step 8: Connect Cursor to the Dev Container

Now for the magic! This connects Cursor to your Docker container so you get full IDE support.

1. **Open Command Palette:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
   - You'll see a search box appear at the top of Cursor

2. **Type:** `Reopen in Container`
   - You should see: **"Dev Containers: Reopen in Container"**
   - Click it OR press Enter

3. **Wait for Container to Connect:**
   - Cursor will close and reopen
   - You'll see progress messages at the bottom right: "Starting Dev Container..."
   - **First time takes 2-5 minutes** as it installs extensions inside the container
   - Subsequent times are much faster (30 seconds)

4. **Verify Connection:**
   - Look at the **bottom-left corner** of Cursor
   - You should see a green/blue indicator that says: **"Dev Container: Job Portal - Full Stack"**
   - Open the integrated terminal (`` Ctrl+` `` or View → Terminal)
   - Try these commands:
   ```bash
   python3 --version   # Should show Python 3.11+
   node --version      # Should show Node 20+
   bun --version       # Should show Bun
   ```

**✅ Success Check:**
- Bottom-left shows "Dev Container: Job Portal - Full Stack"
- Terminal commands show correct versions
- You can browse files in the sidebar with no errors

---

### Step 9: Start Developing!

You're all set! Here's what you can do now:

**Create Your Feature Branch:**
```bash
# In Cursor's integrated terminal:
git checkout -b feature-yourname-description

# Example:
git checkout -b feature-john-user-authentication
```

**Edit Files:**
- Browse to `frontend/src/` for frontend code
- Browse to `backend/app/` for backend code
- All TypeScript and Python code will have:
  - ✅ Auto-completion
  - ✅ Type checking
  - ✅ Error highlighting
  - ✅ Auto-formatting on save

**View Your Changes:**
- Frontend: http://localhost:3000 (auto-reloads when you save files)
- Backend API: http://localhost:8000/docs (auto-reloads when you save files)

---

## Project Structure

```
Job-Portal/
├── .devcontainer/          # VSCode dev container configuration
├── frontend/               # Next.js application
├── backend/                # FastAPI application
├── docker-compose.yml      # Docker orchestration
└── .env                    # Environment configuration
```

## Available Services

| Service    | URL                          | Container Name          |
|------------|------------------------------|-------------------------|
| Frontend   | http://localhost:3000        | job-portal-frontend     |
| Backend    | http://localhost:8000        | job-portal-backend      |
| ChromaDB   | http://localhost:8001        | job-portal-chromadb     |
| Redis      | redis://localhost:6379       | job-portal-redis        |

## 🔄 Common Commands

### Stop All Services
When you're done working for the day:
```bash
# In the terminal where docker compose is running:
Press Ctrl+C to stop

# Or in any terminal:
docker compose down
```

### Start Services Again (Next Day)
```bash
# Navigate to project folder
cd ~/Documents/Job-Portal  # Adjust path as needed

# Start containers
docker compose up
```

### Rebuild Containers (After Major Changes)
If someone updates Docker files or dependencies:
```bash
docker compose down
docker compose up --build
```

### View Logs (Debugging)
```bash
docker compose logs frontend    # See frontend logs
docker compose logs backend     # See backend logs
docker compose logs chromadb    # See database logs
docker compose logs -f          # Follow all logs in real-time
```

### Update Your Code (Pull Latest Changes)
```bash
# In Cursor's terminal (inside dev container):
git pull origin Dev

# If you have conflicts, ask for help!
```

---

## 🐛 Troubleshooting

### Problem: `docker compose up` fails with "port already in use"

**Solution:** Another service is using ports 3000, 8000, 5432, or 6379.

```bash
# Stop all containers and try again:
docker compose down
docker compose up
```

If that doesn't work, find what's using the port:
```bash
# Mac/Linux:
lsof -i :3000    # Check port 3000
lsof -i :8000    # Check port 8000

# Windows (PowerShell):
netstat -ano | findstr :3000
```

---

### Problem: "Dev Container" option doesn't appear in Cursor

**Solution:**

1. Make sure you installed the **"Dev Containers"** extension (Step 7)
2. Restart Cursor completely
3. Try `Cmd+Shift+P` → Type `Dev Containers: Reopen in Container`

---

### Problem: Docker is slow or uses too much memory

**Solution:** Increase Docker's memory allocation:

1. Open Docker Desktop
2. Click Settings (gear icon)
3. Go to Resources
4. Increase Memory to at least **4 GB** (8 GB recommended)
5. Click "Apply & Restart"

---

### Problem: Frontend shows error "Failed to fetch" or "Cannot connect to backend"

**Solution:** Backend might not be running properly.

```bash
# Check backend logs:
docker compose logs backend

# Look for errors. If you see "Database connection failed", restart:
docker compose down
docker compose up
```

---

### Problem: Changes I make don't show up

**Solution:**

1. Make sure you saved the file (`Cmd+S` / `Ctrl+S`)
2. Check browser console for errors (F12)
3. Hard refresh browser (`Cmd+Shift+R` / `Ctrl+Shift+R`)
4. Check terminal logs for errors:
   ```bash
   docker compose logs -f frontend
   docker compose logs -f backend
   ```

---

### Problem: Git says "Permission denied" or "Authentication failed"

**Solution:** You need to set up Git authentication.

**If using HTTPS:**
```bash
# Configure your Git username and email:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Then when you push, GitHub will ask for your **Personal Access Token** (not your password!).
[How to create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

**If using SSH:**
Ask your team lead for help setting up SSH keys.

---

### Problem: "Module not found" or "Cannot find package"

**Solution:** Dependencies might not be installed.

```bash
# Rebuild containers to reinstall dependencies:
docker compose down
docker compose up --build
```

---

### Problem: I accidentally broke something and don't know how to fix it

**Solution:** Reset to the last working version.

```bash
# Discard all your local changes (BE CAREFUL - this deletes your work!):
git reset --hard HEAD

# Or stash your changes to save them for later:
git stash

# Get the latest code from the team:
git pull origin Dev
```

**Ask for help before doing this if you're unsure!**

---

## 📖 Additional Resources

- **Next.js Docs:** https://nextjs.org/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Docker Docs:** https://docs.docker.com
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Git Basics:** https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

---

## 🌿 Team Branching Strategy

We use a simple three-branch workflow:

```
main (production-ready code)
  ↑
Dev (integration/testing branch)
  ↑
feature-yourname-description (your work)
```

### Step-by-Step Workflow:

**1. Start Your Feature (First Time)**
```bash
# Make sure you're on the Dev branch first
git checkout Dev

# Get the latest code
git pull origin Dev

# Create your feature branch
git checkout -b feature-yourname-description

# Example:
git checkout -b feature-john-add-login-page
```

**2. Make Your Changes**
- Edit files in Cursor
- Save your work frequently
- Test in browser (http://localhost:3000 and http://localhost:8000/docs)

**3. Commit Your Changes**
```bash
# See what files you changed
git status

# Add files to commit
git add .

# Commit with a descriptive message
git commit -m "Add login page with email and password fields"

# Push to GitHub
git push origin feature-yourname-description
```

**4. Create a Pull Request (PR)**
1. Go to the GitHub repository in your browser
2. You'll see a yellow banner: "Compare & pull request"
3. Click it
4. Make sure:
   - Base branch: `Dev` (not `main`!)
   - Compare branch: `feature-yourname-description`
5. Write a description of what you did
6. Click "Create Pull Request"
7. Ask team lead to review

**5. After PR is Merged**
```bash
# Switch back to Dev branch
git checkout Dev

# Get the latest code (including your merged changes)
git pull origin Dev

# Delete your old feature branch (you're done with it!)
git branch -d feature-yourname-description
```

**Then start a new feature branch for your next task!**

---

## ❓ Getting Help

If you're stuck:

1. **Check this README** - Especially the Troubleshooting section
2. **Check Docker logs** - Run `docker compose logs -f` to see errors
3. **Ask your team** - Someone probably had the same problem!
4. **Create an issue** - If it's a bug, create a GitHub issue
5. **Contact team lead** - They're here to help!

**Before asking for help, try to:**
- Describe what you were trying to do
- Explain what happened instead
- Share any error messages you see
- Mention what you already tried

---

## 🎯 Quick Reference Cheat Sheet

### First Time Setup
```bash
# 1. Clone repo
git clone <repo-url>
cd Job-Portal

# 2. Create .env
cp .env.example .env

# 3. Build and start (automatically builds first time)
docker compose up

# 4. In Cursor: Cmd+Shift+P → "Reopen in Container"
```

### Daily Workflow
```bash
# Start your day
docker compose up                              # Start all services
cursor .                                       # Open project
# Cmd+Shift+P → "Reopen in Container"         # Connect to container

# Work on feature
git checkout Dev                               # Switch to Dev branch
git pull origin Dev                            # Get latest code
git checkout -b feature-yourname-description   # Create feature branch
# ... make changes ...
git add .                                      # Stage changes
git commit -m "Descriptive message"            # Commit
git push origin feature-yourname-description   # Push to GitHub

# End your day
Ctrl+C                                         # Stop docker (in terminal)
docker compose down                            # Or use this
```

### When Things Need Rebuilding
```bash
# Someone updated dependencies (package.json, requirements.txt, Dockerfiles)
docker compose down
docker compose up --build
```

### Quick Checks
```bash
docker compose logs -f              # See all logs
docker compose logs backend         # See backend logs only
docker ps                           # See running containers
git status                          # See your changes
git branch                          # See current branch
```

### Extensions to Install in Cursor
- **Dev Containers** by Anysphere (Cmd+Shift+X to open Extensions)

---

Good luck and happy coding! 🚀