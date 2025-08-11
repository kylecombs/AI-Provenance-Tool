from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class SimilarArtwork(BaseModel):
    artwork_id: int
    title: str
    year: Optional[int]
    format_type: Optional[str]
    similarity_score: float
    image_url: Optional[str] = None

class MatchesResponse(BaseModel):
    detection_id: int
    detected_artwork_id: int
    detected_artwork_title: str
    confidence_score: float
    similar_artworks: List[SimilarArtwork]
    match_count: int

class ConfirmMatchRequest(BaseModel):
    confirmed_artwork_id: int
    user_notes: Optional[str] = None

class ConfirmMatchResponse(BaseModel):
    detection_id: int
    original_artwork_id: int
    confirmed_artwork_id: int
    provenance_record_id: int
    message: str

class ProvenanceEntry(BaseModel):
    exhibition_id: int
    exhibition_name: str
    venue: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    detection_confidence: float
    detected_at: datetime

class ProvenanceResponse(BaseModel):
    artwork_id: int
    artwork_title: str
    artwork_year: Optional[int]
    provenance_entries: List[ProvenanceEntry]
    total_exhibitions: int
    date_range: Optional[str] = None  # e.g., "2020-2023"

class ProvenanceExportRequest(BaseModel):
    artwork_id: int
    format: str = "json"  # json, csv, pdf
    include_images: bool = False

class ProvenanceExportResponse(BaseModel):
    artwork_id: int
    export_url: str
    format: str
    expires_at: datetime