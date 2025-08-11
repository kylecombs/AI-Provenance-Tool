from app.core.database import get_db
from app.models import Artwork, Detection, Exhibition, ProvenanceRecord
from app.schemas import (ConfirmMatchRequest, ConfirmMatchResponse,
                         MatchesResponse, ProvenanceEntry, ProvenanceResponse,
                         SimilarArtwork)
from app.services.vector_service import vector_service
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

router = APIRouter(prefix="/results", tags=["results"])

@router.get("/matches/{detection_id}", response_model=MatchesResponse)
async def get_similarity_matches(detection_id: int, db: Session = Depends(get_db)):
    """Get similarity matches for a detection"""
    
    # Get the detection with artwork info
    detection = db.query(Detection).join(Artwork).filter(
        Detection.id == detection_id
    ).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    similar_artworks = []
    
    # If vector service is available, find similar artworks
    if vector_service.is_available() and detection.artwork.vector_embedding:
        try:
            # Search for similar artworks using the detected artwork's embedding
            matches = vector_service.search_similar_artworks(
                query_embedding=detection.artwork.vector_embedding,
                top_k=10,
                score_threshold=0.5
            )
            
            for artwork_id_str, similarity_score, _ in matches:
                artwork_id = int(artwork_id_str)
                
                # Skip the same artwork
                if artwork_id == detection.artwork_id:
                    continue
                
                # Get full artwork details from database
                artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
                if artwork:
                    similar_artworks.append(SimilarArtwork(
                        artwork_id=artwork.id,
                        title=artwork.title,
                        year=artwork.year,
                        format_type=artwork.format_type,
                        similarity_score=similarity_score,
                        image_url=artwork.image_url
                    ))
        
        except Exception as e:
            print(f"Error searching similar artworks: {e}")
            # Fall back to basic database query if vector search fails
    
    # If no vector matches or vector service unavailable, use basic similarity
    if not similar_artworks:
        # Find artworks with similar metadata
        similar_db_artworks = db.query(Artwork).filter(
            Artwork.id != detection.artwork_id
        )
        
        # Add similarity filters
        if detection.artwork.format_type:
            similar_db_artworks = similar_db_artworks.filter(
                Artwork.format_type == detection.artwork.format_type
            )
        
        if detection.artwork.year:
            # Find artworks within 20 years
            year_range = 20
            similar_db_artworks = similar_db_artworks.filter(
                Artwork.year.between(
                    detection.artwork.year - year_range,
                    detection.artwork.year + year_range
                )
            )
        
        # Get first 5 matches
        for artwork in similar_db_artworks.limit(5).all():
            # Calculate mock similarity score based on metadata
            similarity_score = 0.6  # Base score
            
            if artwork.format_type == detection.artwork.format_type:
                similarity_score += 0.2
            
            if artwork.year and detection.artwork.year:
                year_diff = abs(artwork.year - detection.artwork.year)
                if year_diff <= 5:
                    similarity_score += 0.15
                elif year_diff <= 10:
                    similarity_score += 0.1
            
            similar_artworks.append(SimilarArtwork(
                artwork_id=artwork.id,
                title=artwork.title,
                year=artwork.year,
                format_type=artwork.format_type,
                similarity_score=min(similarity_score, 0.95),  # Cap at 0.95
                image_url=artwork.image_url
            ))
    
    return MatchesResponse(
        detection_id=detection_id,
        detected_artwork_id=detection.artwork_id,
        detected_artwork_title=detection.artwork.title,
        confidence_score=detection.confidence_score,
        similar_artworks=similar_artworks,
        match_count=len(similar_artworks)
    )

@router.post("/matches/{detection_id}/confirm", response_model=ConfirmMatchResponse)
async def confirm_match(
    detection_id: int,
    request: ConfirmMatchRequest,
    db: Session = Depends(get_db)
):
    """Confirm a match and create provenance record"""
    
    # Get the detection
    detection = db.query(Detection).join(
        Artwork, Detection.artwork_id == Artwork.id
    ).filter(Detection.id == detection_id).first()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    # Verify the confirmed artwork exists
    confirmed_artwork = db.query(Artwork).filter(
        Artwork.id == request.confirmed_artwork_id
    ).first()
    
    if not confirmed_artwork:
        raise HTTPException(status_code=404, detail="Confirmed artwork not found")
    
    # Get the exhibition from the installation photo
    installation_photo = detection.installation_photo
    exhibition_id = installation_photo.exhibition_id
    
    # Check if provenance record already exists
    existing_record = db.query(ProvenanceRecord).filter(
        ProvenanceRecord.detection_id == detection_id
    ).first()
    
    if existing_record:
        # Update existing record
        existing_record.artwork_id = request.confirmed_artwork_id
        provenance_record = existing_record
    else:
        # Create new provenance record
        provenance_record = ProvenanceRecord()
        provenance_record.artwork_id = request.confirmed_artwork_id
        provenance_record.exhibition_id = exhibition_id
        provenance_record.detection_id = detection_id
        db.add(provenance_record)
    
    # Update the detection to point to confirmed artwork if different
    original_artwork_id = detection.artwork_id
    if detection.artwork_id != request.confirmed_artwork_id:
        detection.artwork_id = request.confirmed_artwork_id
    
    db.commit()
    db.refresh(provenance_record)
    
    return ConfirmMatchResponse(
        detection_id=detection_id,
        original_artwork_id=original_artwork_id,
        confirmed_artwork_id=request.confirmed_artwork_id,
        provenance_record_id=provenance_record.id,
        message="Match confirmed and provenance record created"
    )

@router.get("/provenance/{artwork_id}", response_model=ProvenanceResponse)
async def get_artwork_provenance(artwork_id: int, db: Session = Depends(get_db)):
    """Get exhibition history for an artwork"""
    
    # Verify artwork exists
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Get all provenance records for this artwork
    provenance_records = db.query(ProvenanceRecord).join(
        Exhibition, ProvenanceRecord.exhibition_id == Exhibition.id
    ).join(
        Detection, ProvenanceRecord.detection_id == Detection.id
    ).filter(
        ProvenanceRecord.artwork_id == artwork_id
    ).order_by(desc(ProvenanceRecord.created_at)).all()
    
    # Build provenance entries
    provenance_entries = []
    years = []
    
    for record in provenance_records:
        exhibition = record.exhibition
        detection = record.detection
        
        # Format dates
        start_date_str = exhibition.start_date.isoformat() if exhibition.start_date else None
        end_date_str = exhibition.end_date.isoformat() if exhibition.end_date else None
        
        # Track years for date range calculation
        if exhibition.start_date:
            years.append(exhibition.start_date.year)
        if exhibition.end_date:
            years.append(exhibition.end_date.year)
        
        provenance_entries.append(ProvenanceEntry(
            exhibition_id=exhibition.id,
            exhibition_name=exhibition.name,
            venue=exhibition.venue,
            start_date=start_date_str,
            end_date=end_date_str,
            detection_confidence=detection.confidence_score,
            detected_at=record.created_at
        ))
    
    # Calculate date range
    date_range = None
    if years:
        min_year = min(years)
        max_year = max(years)
        if min_year == max_year:
            date_range = str(min_year)
        else:
            date_range = f"{min_year}-{max_year}"
    
    return ProvenanceResponse(
        artwork_id=artwork_id,
        artwork_title=artwork.title,
        artwork_year=artwork.year,
        provenance_entries=provenance_entries,
        total_exhibitions=len(provenance_entries),
        date_range=date_range
    )