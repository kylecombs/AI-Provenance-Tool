"""
Type stubs for SQLAlchemy models.

Note: We intentionally annotate mapped attributes as Any so static type checkers
do not treat them as plain Python types (e.g., str), which would break SQLAlchemy
expression APIs like .ilike(), .in_(), and .is_(None) in query filters.
"""
from datetime import date, datetime
from typing import Any, List, Optional

class Artwork:
    id: Any
    title: Any
    year: Any
    format_type: Any
    dimensions: Any
    image_url: Any
    vector_embedding: Any

class Exhibition:
    id: Any
    name: Any
    venue: Any
    start_date: Any
    end_date: Any

class InstallationPhoto:
    id: Any
    exhibition_id: Any
    photo_url: Any
    processed_status: Any
    exhibition: Any
    detections: Any

class Detection:
    id: Any
    installation_photo_id: Any
    artwork_id: Any
    confidence_score: Any
    bounding_box: Optional[dict[str, Any]]
    artwork: Artwork
    installation_photo: InstallationPhoto

class ProvenanceRecord:
    id: Any
    artwork_id: Any
    exhibition_id: Any
    detection_id: Any
    created_at: Any
    artwork: Artwork
    exhibition: Exhibition
    detection: Detection