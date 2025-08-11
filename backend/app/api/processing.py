import asyncio
import random
import uuid
from datetime import datetime
from typing import Any, Dict

from app.core.database import get_db
from app.models import Artwork, Detection, Exhibition, InstallationPhoto
from app.schemas import (BoundingBox, DetectionResponse,
                         PhotoDetectionsResponse, ProcessingStatus,
                         ProcessingStatusResponse,
                         ProcessInstallationPhotoRequest,
                         ProcessInstallationPhotoResponse)
from app.services.vector_service import vector_service
from app.utils.embedding_utils import generate_mock_embedding
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/process", tags=["processing"])

# In-memory job tracking for the POC (use Redis in production)
job_status: Dict[str, Dict[str, Any]] = {}

async def mock_process_installation_photo(
    job_id: str,
    installation_photo_id: int,
    photo_url: str,
):
    """
    Mock background processing function.
    In production, this would:
    1. Download the image from photo_url
    2. Run computer vision models to detect artworks
    3. Generate embeddings for detected regions
    4. Query vector database for matches
    5. Store detections with confidence scores
    """
    
    # Update job status
    job_status[job_id]["status"] = ProcessingStatus.PROCESSING
    job_status[job_id]["progress_percentage"] = 10
    job_status[job_id]["message"] = "Downloading and analyzing image..."
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    try:
        # Create new database session for background task
        from app.core.database import SessionLocal
        db = SessionLocal()
        
        # Update progress
        job_status[job_id]["progress_percentage"] = 50
        job_status[job_id]["message"] = "Detecting artworks in image..."
        
        # Get all artworks for potential matches
        artworks = db.query(Artwork).limit(10).all()  # Limit for demo
        
        if not artworks:
            raise Exception("No artworks in catalog to match against")
        
        # Mock detection results - randomly detect 1-3 artworks
        num_detections = random.randint(1, min(3, len(artworks)))
        detected_artworks = random.sample(artworks, num_detections)
        
        job_status[job_id]["progress_percentage"] = 80
        job_status[job_id]["message"] = "Creating detection records..."
        
        # Create detection records
        for i, artwork in enumerate(detected_artworks):
            # Generate mock bounding box
            x = random.randint(50, 400)
            y = random.randint(50, 300)
            width = random.randint(100, 300)
            height = random.randint(100, 400)
            
            # Generate mock confidence score
            confidence = random.uniform(0.75, 0.98)
            
            detection = Detection()
            detection.installation_photo_id = installation_photo_id
            detection.artwork_id = artwork.id
            detection.confidence_score = confidence
            detection.bounding_box = {
                "x": x,
                "y": y,
                "width": width,
                "height": height
            }
            db.add(detection)
        
        # Update installation photo status
        installation_photo = db.query(InstallationPhoto).filter(
            InstallationPhoto.id == installation_photo_id
        ).first()
        
        if installation_photo:
            installation_photo.processed_status = ProcessingStatus.COMPLETED
        
        db.commit()
        
        # Update job status
        job_status[job_id]["status"] = ProcessingStatus.COMPLETED
        job_status[job_id]["progress_percentage"] = 100
        job_status[job_id]["message"] = f"Successfully detected {num_detections} artworks"
        job_status[job_id]["completed_at"] = datetime.now()
        
    except Exception as e:
        # Update job status on error
        job_status[job_id]["status"] = ProcessingStatus.FAILED
        job_status[job_id]["error_details"] = str(e)
        job_status[job_id]["message"] = "Processing failed"
        job_status[job_id]["completed_at"] = datetime.now()
        
        # Update installation photo status
        try:
            installation_photo = db.query(InstallationPhoto).filter(
                InstallationPhoto.id == installation_photo_id
            ).first()
            if installation_photo:
                installation_photo.processed_status = ProcessingStatus.FAILED
            db.commit()
        except:
            pass
    
    finally:
        db.close()

@router.post("/installation-photo", response_model=ProcessInstallationPhotoResponse)
async def process_installation_photo(
    request: ProcessInstallationPhotoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit photo for processing"""
    
    # Verify exhibition exists
    exhibition = db.query(Exhibition).filter(Exhibition.id == request.exhibition_id).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    # Create installation photo record
    installation_photo = InstallationPhoto()
    installation_photo.exhibition_id = request.exhibition_id
    installation_photo.photo_url = request.photo_url
    installation_photo.processed_status = ProcessingStatus.PENDING
    db.add(installation_photo)
    db.commit()
    db.refresh(installation_photo)
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_status[job_id] = {
        "installation_photo_id": installation_photo.id,
        "status": ProcessingStatus.PENDING,
        "progress_percentage": 0,
        "message": "Photo queued for processing",
        "error_details": None,
        "started_at": datetime.now(),
        "completed_at": None
    }
    
    # Start background processing
    background_tasks.add_task(
        mock_process_installation_photo,
        job_id,
        installation_photo.id,
        request.photo_url,
    )
    
    return ProcessInstallationPhotoResponse(
        job_id=job_id,
        installation_photo_id=installation_photo.id,
        status=ProcessingStatus.PENDING,
        message="Photo submitted for processing"
    )

@router.get("/status/{job_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(job_id: str):
    """Check processing status"""
    
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_info = job_status[job_id]
    
    return ProcessingStatusResponse(
        job_id=job_id,
        installation_photo_id=job_info["installation_photo_id"],
        status=job_info["status"],
        progress_percentage=job_info.get("progress_percentage"),
        message=job_info.get("message"),
        error_details=job_info.get("error_details"),
        started_at=job_info["started_at"],
        completed_at=job_info.get("completed_at")
    )

@router.get("/detections/{photo_id}", response_model=PhotoDetectionsResponse)
async def get_photo_detections(photo_id: int, db: Session = Depends(get_db)):
    """Get all detections for a photo"""
    
    # Get installation photo with exhibition info
    installation_photo = db.query(InstallationPhoto).join(Exhibition).filter(
        InstallationPhoto.id == photo_id
    ).first()
    
    if not installation_photo:
        raise HTTPException(status_code=404, detail="Installation photo not found")
    
    # Get detections with artwork info
    detections = db.query(Detection).join(Artwork).filter(
        Detection.installation_photo_id == photo_id
    ).all()
    
    # Format detection responses
    detection_responses = []
    for detection in detections:
        bounding_box = None
        if detection.bounding_box:
            bounding_box = BoundingBox(**detection.bounding_box)
        
        detection_responses.append(DetectionResponse(
            id=detection.id,
            installation_photo_id=detection.installation_photo_id,
            artwork_id=detection.artwork_id,
            confidence_score=detection.confidence_score,
            bounding_box=bounding_box,
            artwork_title=detection.artwork.title,
            artwork_year=detection.artwork.year
        ))
    
    return PhotoDetectionsResponse(
        installation_photo_id=photo_id,
        photo_url=installation_photo.photo_url,
        exhibition_name=installation_photo.exhibition.name,
        processed_status=installation_photo.processed_status,
        detections=detection_responses,
        detection_count=len(detection_responses)
    )