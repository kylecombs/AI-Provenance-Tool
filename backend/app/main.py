from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import (
    ErrorHandlingMiddleware,
    RequestLoggingMiddleware,
    CacheControlMiddleware
)
from app.api import api_router

# Setup logging first
setup_logging()
logger = get_logger("main")

app = FastAPI(
    title="AI Provenance Tool",
    description="AI-powered artwork identification in installation photos",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# Add custom middleware (order matters - first added is outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CacheControlMiddleware)

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

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Provenance Tool API starting up...")
    logger.info(f"Environment: {settings.SECRET_KEY[:10]}..." if settings.SECRET_KEY else "No secret key set")
    

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("🛑 AI Provenance Tool API shutting down...")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
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
    from app.core.database import engine
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "services": {}
    }
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
        logger.debug("Database health check: OK")
    except Exception as e:
        health_status["services"]["database"] = "disconnected"
        health_status["status"] = "unhealthy"
        logger.error(f"Database health check failed: {e}")
    
    # Check vector service
    if vector_service.is_available():
        health_status["services"]["vector_service"] = "connected"
        logger.debug("Vector service health check: OK")
    else:
        health_status["services"]["vector_service"] = "unavailable"
        logger.warning("Vector service health check: unavailable")
    
    # Add Redis check (placeholder)
    health_status["services"]["redis"] = "not_implemented"
    
    # Set timestamp
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    logger.info(f"Health check completed: {health_status['status']}")
    return health_status
