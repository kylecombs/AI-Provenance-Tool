from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessInstallationPhotoRequest(BaseModel):
    exhibition_id: int
    photo_url: str

class ProcessInstallationPhotoResponse(BaseModel):
    job_id: str
    installation_photo_id: int
    status: ProcessingStatus
    message: str

class ProcessingStatusResponse(BaseModel):
    job_id: str
    installation_photo_id: int
    status: ProcessingStatus
    progress_percentage: Optional[int] = None
    message: Optional[str] = None
    error_details: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class DetectionResponse(BaseModel):
    id: int
    installation_photo_id: int
    artwork_id: int
    confidence_score: float
    bounding_box: Optional[BoundingBox] = None
    artwork_title: Optional[str] = None
    artwork_year: Optional[int] = None
    
    class Config:
        from_attributes = True

class PhotoDetectionsResponse(BaseModel):
    installation_photo_id: int
    photo_url: str
    exhibition_name: str
    processed_status: ProcessingStatus
    detections: List[DetectionResponse]
    detection_count: int