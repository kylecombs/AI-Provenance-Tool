from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False, index=True)
    exhibition_id = Column(Integer, ForeignKey("exhibitions.id"), nullable=False, index=True) 
    detection_id = Column(Integer, ForeignKey("detections.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    artwork = relationship("Artwork", back_populates="provenance_records")
    exhibition = relationship("Exhibition", back_populates="provenance_records")
    detection = relationship("Detection", back_populates="provenance_record")