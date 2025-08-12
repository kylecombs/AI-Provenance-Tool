"""Error response schemas for the AI Provenance Tool API"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    message: str
    type: str
    request_id: Optional[str] = None
    timestamp: Optional[str] = None


class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field details"""
    details: List[ErrorDetail]


class DatabaseErrorResponse(ErrorResponse):
    """Database error response"""
    operation: Optional[str] = None
    table: Optional[str] = None


class ServiceUnavailableErrorResponse(ErrorResponse):
    """Service unavailable error response"""
    service: str
    retry_after: Optional[int] = None  # Seconds to wait before retry


class ProcessingErrorResponse(ErrorResponse):
    """Processing error response"""
    job_id: Optional[str] = None
    stage: Optional[str] = None  # Which processing stage failed


class APIErrorResponse(ErrorResponse):
    """External API error response"""
    service: str
    status_code: int
    details: Optional[Dict[str, Any]] = None


# Common error responses for OpenAPI documentation
COMMON_ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Bad Request",
                    "message": "Invalid request parameters",
                    "type": "validation_error",
                    "request_id": "abc123"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Unauthorized",
                    "message": "Invalid API key",
                    "type": "authentication_error",
                    "request_id": "abc123"
                }
            }
        }
    },
    403: {
        "description": "Forbidden", 
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Forbidden",
                    "message": "Insufficient permissions",
                    "type": "authorization_error",
                    "request_id": "abc123"
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Not Found", 
                    "message": "Resource not found",
                    "type": "not_found_error",
                    "request_id": "abc123"
                }
            }
        }
    },
    422: {
        "description": "Validation Error",
        "model": ValidationErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Validation Error",
                    "message": "Request validation failed",
                    "type": "validation_error",
                    "request_id": "abc123",
                    "details": [
                        {
                            "field": "title",
                            "message": "Field required",
                            "code": "missing"
                        }
                    ]
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "type": "internal_error",
                    "request_id": "abc123"
                }
            }
        }
    },
    503: {
        "description": "Service Unavailable",
        "model": ServiceUnavailableErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": "Service Unavailable",
                    "message": "Vector service is currently unavailable",
                    "type": "service_unavailable",
                    "service": "pinecone",
                    "retry_after": 60,
                    "request_id": "abc123"
                }
            }
        }
    }
}