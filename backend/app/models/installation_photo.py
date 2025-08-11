from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ProcessedStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class InstallationPhoto(Base):
    __tablename__ = "installation_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False, index=True)
    photo_url = Column(String, nullable=False)
    processed_status = Column(Enum(ProcessedStatus), default=ProcessedStatus.PENDING, index=True)
    
    # Relationships
    exhibition = relationship("Exhibition", back_populates="installation_photos")
    detections = relationship("Detection", back_populates="installation_photo")