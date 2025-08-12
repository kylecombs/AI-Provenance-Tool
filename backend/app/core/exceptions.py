"""Custom exceptions for the AI Provenance Tool API"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AIProvenanceException(Exception):
    """Base exception for AI Provenance Tool"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(AIProvenanceException):
    """Database related exceptions"""
    pass


class VectorServiceException(AIProvenanceException):
    """Vector service (Pinecone) related exceptions"""
    pass


class ProcessingException(AIProvenanceException):
    """Image processing related exceptions"""
    pass


class ValidationException(AIProvenanceException):
    """Data validation exceptions"""
    pass


# HTTP Exceptions for FastAPI
class ArtworkNotFoundException(HTTPException):
    def __init__(self, artwork_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with ID {artwork_id} not found"
        )


class ExhibitionNotFoundException(HTTPException):
    def __init__(self, exhibition_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exhibition with ID {exhibition_id} not found"
        )


class DetectionNotFoundException(HTTPException):
    def __init__(self, detection_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection with ID {detection_id} not found"
        )


class JobNotFoundException(HTTPException):
    def __init__(self, job_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found"
        )


class VectorServiceUnavailableException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector service is currently unavailable. Please check Pinecone configuration."
        )


class InvalidFileFormatException(HTTPException):
    def __init__(self, file_format: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {file_format}. Supported formats: jpg, jpeg, png, gif"
        )


class ProcessingFailedException(HTTPException):
    def __init__(self, reason: str = "Processing failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {reason}"
        )


class InsufficientPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action"
        )