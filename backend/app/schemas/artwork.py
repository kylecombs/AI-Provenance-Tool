from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ArtworkBase(BaseModel):
    title: str
    year: Optional[int] = None
    format_type: Optional[str] = None
    dimensions: Optional[str] = None
    image_url: Optional[str] = None

class ArtworkCreate(ArtworkBase):
    pass

class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    format_type: Optional[str] = None
    dimensions: Optional[str] = None
    image_url: Optional[str] = None

class ArtworkResponse(ArtworkBase):
    id: int
    vector_embedding: Optional[List[float]] = None
    
    class Config:
        from_attributes = True

class ArtworkListResponse(BaseModel):
    artworks: List[ArtworkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class BulkEmbedRequest(BaseModel):
    artwork_ids: Optional[List[int]] = None  # If None, process all artworks
    force_regenerate: bool = False  # Whether to regenerate existing embeddings

class BulkEmbedResponse(BaseModel):
    processed_count: int
    failed_count: int
    message: str
    failed_artwork_ids: Optional[List[int]] = None