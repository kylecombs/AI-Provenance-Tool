"""Middleware for error handling, logging, and request processing"""

import logging
import time
import traceback
import uuid
from typing import Callable

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    AIProvenanceException,
    DatabaseException,
    VectorServiceException,
    ProcessingException,
    ValidationException
)

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Database Error",
                    "message": "An error occurred while accessing the database",
                    "type": "database_error"
                }
            )
        except AIProvenanceException as e:
            logger.error(f"AI Provenance error: {e.message}", extra={"details": e.details})
            return JSONResponse(
                status_code=400,
                content={
                    "error": "AI Provenance Error",
                    "message": e.message,
                    "details": e.details,
                    "type": type(e).__name__.lower()
                }
            )
        except Exception as e:
            # Log the full traceback for unexpected errors
            error_id = str(uuid.uuid4())
            logger.error(
                f"Unexpected error [{error_id}]: {str(e)}",
                exc_info=True,
                extra={"error_id": error_id}
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "error_id": error_id,
                    "type": "internal_error"
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request and response logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                },
                exc_info=True
            )
            raise


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add cache control headers for static content"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add cache headers for static content
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        elif request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response