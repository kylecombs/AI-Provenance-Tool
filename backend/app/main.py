from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router

app = FastAPI(
    title="AI Provenance Tool",
    description="AI-powered artwork identification in installation photos",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "AI Provenance Tool API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    from app.services.vector_service import vector_service
    
    # Check vector service status
    vector_status = "connected" if vector_service.is_available() else "unavailable"
    
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "vector_service": vector_status
    }
