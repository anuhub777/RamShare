from typing import List
from fastapi import APIRouter, Depends
from app.schemas.marketplace import MarketplaceStats, AvailableResource
from app.services.marketplace_service import MarketplaceService
from app.dependencies import get_marketplace_service

router = APIRouter()

@router.get("/statistics", response_model=MarketplaceStats)
async def get_statistics(service: MarketplaceService = Depends(get_marketplace_service)):
    return await service.get_statistics()

@router.get("/resources", response_model=List[AvailableResource])
async def get_resources(service: MarketplaceService = Depends(get_marketplace_service)):
    return await service.get_available_resources()
