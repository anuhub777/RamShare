import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import auth, providers, jobs, credits, marketplace
from app.dependencies import get_storage_instance, set_storage_instance, get_queue_instance
from app.services.matchmaking_service import MatchmakingService
from app.services.provider_service import ProviderService

logger = logging.getLogger("ramshare")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

async def background_loop():
    logger.info("Starting background matchmaking and provider monitor...")
    storage = get_storage_instance()
    queue = get_queue_instance()
    matchmaking = MatchmakingService(storage, queue)
    provider_svc = ProviderService(storage)

    stale_check_counter = 0
    while True:
        try:
            await matchmaking.process_job_queue()
        except Exception as e:
            logger.error(f"Error in matchmaking loop: {e}")

        stale_check_counter += 1
        if stale_check_counter >= 6:  # every 30 seconds
            stale_check_counter = 0
            try:
                await provider_svc.check_stale_providers()
            except Exception as e:
                logger.error(f"Error checking stale providers: {e}")

        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    storage = get_storage_instance()
    await storage.initialize()
    bg_task = asyncio.create_task(background_loop())
    yield
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        pass

def create_app(storage_override=None) -> FastAPI:
    if storage_override is not None:
        set_storage_instance(storage_override)

    application = FastAPI(
        title="RAMShare API",
        description="Decentralized Peer-to-Peer Cloud Computing Marketplace API",
        version="1.0.0",
        lifespan=lifespan if storage_override is None else None
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth.router, prefix="/auth", tags=["Auth"])
    application.include_router(providers.router, prefix="/providers", tags=["Providers"])
    application.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
    application.include_router(credits.router, prefix="/credits", tags=["Credits"])
    application.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])

    @application.get("/health")
    async def health():
        return {"status": "ok", "service": "ramshare-backend"}

    @application.get("/install.sh")
    async def root_install_script(request: Request):
        return await providers.get_install_script(request)

    # Serve static frontend if available
    static_dir = os.environ.get("RAMSHARE_STATIC_DIR") or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
    )
    if os.path.isdir(static_dir):
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.isdir(assets_dir):
            application.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @application.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            target = os.path.join(static_dir, full_path)
            if full_path and os.path.isfile(target):
                return FileResponse(target)
            index_file = os.path.join(static_dir, "index.html")
            if os.path.isfile(index_file):
                return FileResponse(index_file)
            return {"detail": "Frontend build not found"}

    return application

app = create_app()
