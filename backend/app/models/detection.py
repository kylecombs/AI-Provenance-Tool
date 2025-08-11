from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Detection(Base):
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    installation_photo_id = Column(Integer, ForeignKey("installation_photos.id"), nullable=False, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False, index=True)
    bounding_box = Column(JSON)  # Store as {"x": int, "y": int, "width": int, "height": int}
    
    # Relationships
    installation_photo = relationship("InstallationPhoto", back_populates="detections")
    artwork = relationship("Artwork", back_populates="detections")
    provenance_record = relationship("ProvenanceRecord", back_populates="detection", uselist=False)