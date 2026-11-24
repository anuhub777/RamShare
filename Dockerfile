# Multi-stage Dockerfile for RAMShare Unified Deployment (Frontend + Backend in One Container)

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
# Build production bundle with relative API paths
ENV VITE_API_URL=""
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.11-slim AS runner
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAMSHARE_MODE=local \
    PORT=10000

# Install dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy built frontend assets into the expected directory
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 10000

# Start Uvicorn bound to Render's PORT environment variable
CMD sh -c "cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"
