from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

class Exhibition(Base):
    __tablename__ = "exhibitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    venue = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Relationships
    installation_photos = relationship("InstallationPhoto", back_populates="exhibition")
    provenance_records = relationship("ProvenanceRecord", back_populates="exhibition")