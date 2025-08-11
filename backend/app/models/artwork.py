from sqlalchemy import Column, String, Integer, Float, Text, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base

class Artwork(Base):
    __tablename__ = "artworks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    year = Column(Integer)
    format_type = Column(String)  # e.g., "painting", "sculpture", "photograph"
    dimensions = Column(String)  # e.g., "24x36 inches"
    image_url = Column(Text)
    vector_embedding = Column(ARRAY(Float))  # Store embedding as array of floats
    
    # Relationships
    detections = relationship("Detection", back_populates="artwork")
    provenance_records = relationship("ProvenanceRecord", back_populates="artwork")