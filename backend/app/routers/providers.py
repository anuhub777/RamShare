import io
import os
import zipfile
from fastapi.responses import Response, PlainTextResponse
from fastapi import APIRouter, Depends, status, Request
from app.schemas.provider import (
    ProviderRegisterRequest, ProviderUpdateResources, HeartbeatRequest,
    HeartbeatResponse, ProviderResponse, ProviderListResponse, AvailabilityUpdateRequest
)
from app.schemas.job import JobListResponse, JobResponse
from app.services.provider_service import ProviderService
from app.services.job_service import JobService
from app.models.user import User
from app.dependencies import get_provider_service, get_job_service, get_current_user

router = APIRouter()

@router.get("/agent/download")
async def download_agent_zip():
    """Download the complete ready-to-run provider agent as a ZIP package."""
    agent_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "provider-agent")
    )
    if not os.path.isdir(agent_dir):
        # Fallback if running inside Docker container or alternate path
        agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "provider-agent"))

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(agent_dir):
            if "__pycache__" in root or ".pytest_cache" in root or "venv" in root:
                continue
            for f in files:
                if f.endswith((".pyc", ".db")):
                    continue
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, agent_dir)
                zf.write(full_path, arcname)

    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="ramshare-provider-agent.zip"'}
    )

@router.get("/agent/install.sh")
async def get_install_script(request: Request):
    """Dynamic 1-line bash installer for the provider agent."""
    base_url = str(request.base_url).rstrip("/")
    script = f"""#!/usr/bin/env bash
# ====================================================
#   RAMShare Provider Desktop Agent Automated Installer
# ====================================================
set -e

echo ""
echo "===================================================="
echo "    Installing RAMShare Provider Desktop Agent      "
echo "===================================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required. Please install Python 3.10+."
    exit 1
fi

# 2. Check Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Warning: Docker is not currently running."
    echo "   Provider workloads execute inside isolated Docker containers."
    echo "   Please start Docker Desktop or install Docker Engine."
    echo ""
fi

# 3. Create installation directory
INSTALL_DIR="$HOME/.ramshare-agent"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "📦 Downloading latest provider agent package..."
curl -sSL "{base_url}/providers/agent/download" -o agent.zip
unzip -q -o agent.zip
rm agent.zip

echo "⚙️  Setting up virtual environment and dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet

echo ""
echo "✅ Installation complete!"
echo "🚀 Launching provider agent connected to {base_url}..."
echo ""

python3 -m agent.main start --api-url "{base_url}"
"""
    return PlainTextResponse(script, media_type="text/x-shellscript")

@router.post("/register", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def register_provider(
    request: ProviderRegisterRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    provider = await service.register_provider(current_user.id, request)
    return provider

@router.get("", response_model=ProviderListResponse)
async def list_providers(
    online_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    providers = await service.list_providers(online_only=online_only)
    return ProviderListResponse(providers=providers, total=len(providers))

@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.get_provider(provider_id)

@router.post("/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(
    request: HeartbeatRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.heartbeat(request)

@router.patch("/{provider_id}/availability", response_model=ProviderResponse)
async def set_availability(
    provider_id: str,
    request: AvailabilityUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.set_availability(provider_id, current_user.id, request.is_sharing)

@router.patch("/{provider_id}/resources", response_model=ProviderResponse)
async def update_resources(
    provider_id: str,
    request: ProviderUpdateResources,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.update_resources(provider_id, current_user.id, request)

@router.get("/{provider_id}/jobs", response_model=JobListResponse)
async def get_provider_jobs(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    provider_service: ProviderService = Depends(get_provider_service)
):
    provider = await provider_service.get_provider(provider_id)
    jobs = await job_service.poll_jobs_for_provider(provider_id, current_user.id)
    return JobListResponse(jobs=jobs, total=len(jobs))
