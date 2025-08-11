from fastapi import APIRouter
from .artworks import router as artworks_router
from .processing import router as processing_router  
from .results import router as results_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(artworks_router)
api_router.include_router(processing_router)
api_router.include_router(results_router)

__all__ = ["api_router"]