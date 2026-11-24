# RAMShare Render Deployment Guide

This guide walks you through deploying both the **RAMShare Frontend** (React + Vite) and **Backend** (FastAPI) to [Render](https://render.com).

There are two recommended approaches:

| Approach | Description | Services on Render | Best For |
|---|---|---|---|
| **Option 1: Unified Container (1 Service)** | Single multi-stage Docker container serving both Frontend & Backend on 1 port | 1 Web Service | Single URL, no CORS setup, free-tier friendly |
| **Option 2: Render Blueprint (2 Services)** | Backend Web Service + Frontend Static Site via `render.yaml` | 1 Web Service + 1 Static Site (Free CDN) | Independent scaling, fast static CDN delivery |

---

## Prerequisites

1. A [Render Account](https://render.com).
2. Push your `RamShare` repository to GitHub or GitLab:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of RAMShare"
   git remote add origin https://github.com/<your-username>/ramshare.git
   git push -u origin main
   ```

---

## Option 1: Unified Service (Single Container — Recommended)

In this approach, Render builds both the Vite frontend and FastAPI backend into a single container. FastAPI serves the API endpoints under `/auth`, `/jobs`, `/marketplace`, etc., and automatically serves the React SPA under `/`.

### Steps:

1. Log in to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Web Service**.
3. Connect your Git repository (`ramshare`).
4. Fill in the service configuration:
   - **Name**: `ramshare`
   - **Region**: Choose the closest region (e.g. `Oregon (US West)` or `Frankfurt (EU Central)`)
   - **Runtime**: Select **Docker** (Render will detect the root [Dockerfile](file:///Users/anubhavverma/Downloads/RamShare/Dockerfile))
   - **Plan**: **Free**
5. Add **Environment Variables**:
   | Variable | Value | Description |
   |---|---|---|
   | `RAMSHARE_MODE` | `local` | Uses local SQLite storage |
   | `RAMSHARE_SECRET_KEY` | *(Click "Generate" or enter a 32+ char secret)* | JWT secret key |
   | `RAMSHARE_DB_PATH` | `/tmp/ramshare.db` | SQLite database path |
6. Click **Create Web Service**.
7. Once deployment finishes, your app will be live at `https://ramshare-xxxx.onrender.com`. Both the UI and API work immediately under this single domain!

---

## Option 2: Render Blueprint (Infrastructure-as-Code via `render.yaml`)

RAMShare includes a [render.yaml](file:///Users/anubhavverma/Downloads/RamShare/render.yaml) blueprint file at the root of the repository.

### Steps:

1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** > **Blueprint**.
3. Connect your repository.
4. Render will automatically read `render.yaml` and provision two services:
   - **`ramshare-backend`** (Python Web Service)
   - **`ramshare-frontend`** (Static Site on Render's global CDN)
5. Review the plan settings (both can run on the **Free** tier) and click **Apply**.
6. After provisioning:
   - Copy the backend URL (e.g., `https://ramshare-backend.onrender.com`).
   - Go to the `ramshare-frontend` Static Site settings > **Environment**.
   - Ensure `VITE_API_URL` is set to `https://ramshare-backend.onrender.com`.
   - Trigger a deploy of the frontend so Vite bakes in the backend URL.

---

## Option 3: Manual Dashboard Setup (Separate Services)

If you prefer to configure services manually in the Render UI:

### Part 1: Deploy Backend (Web Service)

1. Click **New +** > **Web Service**.
2. Select your repository.
3. Configure:
   - **Name**: `ramshare-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add Environment Variables:
   - `RAMSHARE_MODE`: `local`
   - `RAMSHARE_SECRET_KEY`: `<generate-random-secret>`
   - `PYTHON_VERSION`: `3.11.9`
5. Click **Create Web Service**.
6. Note down the deployed URL: `https://ramshare-backend.onrender.com`.

### Part 2: Deploy Frontend (Static Site)

1. Click **New +** > **Static Site**.
2. Select your repository.
3. Configure:
   - **Name**: `ramshare-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add Environment Variables:
   - `VITE_API_URL`: `https://ramshare-backend.onrender.com`
5. Configure Redirect/Rewrite (for React Router):
   - Go to **Redirects/Rewrites** in the service settings.
   - Click **Add Rule**:
     - **Type**: `Rewrite`
     - **Source**: `/*`
     - **Destination**: `/index.html`
6. Click **Create Static Site**.

---

## Connecting Provider Agents to Render

Once deployed, provider desktop computers anywhere in the world can register and contribute compute power to your Render-hosted marketplace:

1. On the provider computer, set the backend API URL:
   ```bash
   export RAMSHARE_API_URL="https://ramshare-backend.onrender.com"
   ```
   *(Or if using Option 1, use your unified service URL `https://ramshare-xxxx.onrender.com`)*

2. Run the agent:
   ```bash
   python3 provider-agent/main.py
   ```

3. Choose **1. Register computer** in the interactive menu, then **2. Start sharing compute**. The agent will immediately register with your Render backend and begin streaming heartbeats!

---

## Verifying Deployment

1. **Backend Health Check**:
   ```bash
   curl https://<your-backend-url>/health
   # Response: {"status":"ok","service":"ramshare-backend"}
   ```
2. **Frontend UI**:
   Open `https://<your-frontend-url>` in your browser.
   - Click **Register** to create a test user.
   - Log in and view the Dashboard and Marketplace.
   - Submit a test workload from the **Submit Workload** page.
