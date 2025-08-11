import math
from typing import Optional

from app.core.auth import verify_api_key
from app.core.database import get_db
from app.models import Artwork
from app.schemas import (ArtworkCreate, ArtworkListResponse, ArtworkResponse,
                         ArtworkUpdate, BulkEmbedRequest, BulkEmbedResponse)
from app.services.vector_service import vector_service
from app.utils.embedding_utils import (generate_mock_embedding,
                                       get_artwork_embedding_by_title)
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Depends as FastAPIDepends
from fastapi import HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/artworks", tags=["artworks"])

@router.post("/", response_model=ArtworkResponse, dependencies=[FastAPIDepends(verify_api_key)])
async def create_artwork(
    artwork: ArtworkCreate,
    db: Session = Depends(get_db)
):
    """Upload new artwork to catalog"""
    
    # Generate embedding if image_url is provided
    vector_embedding = None
    if artwork.image_url:
        # In production, this would extract features from the actual image
        vector_embedding = get_artwork_embedding_by_title(str(artwork.title))
        if not vector_embedding:
            # Generate a mock embedding based on artwork metadata
            artwork_hash = hash(f"{artwork.title}{artwork.year}{artwork.format_type}")
            vector_embedding = generate_mock_embedding(abs(artwork_hash) % 10000)
    
    # Create artwork in database
    db_artwork = Artwork(
        **artwork.model_dump()
    )
    if vector_embedding is not None:
        db_artwork.vector_embedding = vector_embedding
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    
    # Store embedding in Pinecone if vector service is available
    if vector_embedding and vector_service.is_available():
        metadata = {
            "title": str(db_artwork.title),
            "year": int(db_artwork.year) if db_artwork.year is not None else None,
            "format_type": str(db_artwork.format_type) if db_artwork.format_type is not None else None,
            "dimensions": str(db_artwork.dimensions) if db_artwork.dimensions is not None else None
        }
        artwork_id: int = db_artwork.id  # type: ignore
        vector_service.upsert_artwork_embedding(
            artwork_id,
            vector_embedding,
            metadata
        )
    
    return db_artwork

@router.get("/", response_model=ArtworkListResponse)
async def list_artworks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title"),
    format_type: Optional[str] = Query(None, description="Filter by format type"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    db: Session = Depends(get_db)
):
    """List all artworks with pagination and filtering"""
    
    # Build query with filters
    query = db.query(Artwork)
    
    if search:
        query = query.filter(Artwork.title.ilike(f"%{search}%"))
    
    if format_type:
        query = query.filter(Artwork.format_type == format_type)
    
    if year_min:
        query = query.filter(Artwork.year >= year_min)
    
    if year_max:
        query = query.filter(Artwork.year <= year_max)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    artworks = query.offset(offset).limit(per_page).all()
    
    # Calculate pagination info
    total_pages = math.ceil(total / per_page)
    
    return ArtworkListResponse(
        artworks=[ArtworkResponse.model_validate(artwork) for artwork in artworks],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Get specific artwork details"""
    
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    return artwork

@router.put("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    artwork_update: ArtworkUpdate,
    db: Session = Depends(get_db)
):
    """Update artwork details"""
    
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Update fields
    update_data = artwork_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(artwork, field, value)
    
    # Regenerate embedding if image_url was updated
    if "image_url" in update_data and update_data["image_url"]:
        vector_embedding = get_artwork_embedding_by_title(str(artwork.title))
        if not vector_embedding:
            artwork_hash = hash(f"{artwork.title}{artwork.year}{artwork.format_type}")
            vector_embedding = generate_mock_embedding(abs(artwork_hash) % 10000)
        
        setattr(artwork, 'vector_embedding', vector_embedding)
        
        # Update Pinecone if available
        if vector_service.is_available():
            metadata = {
                "title": str(artwork.title),
                "year": int(artwork.year) if artwork.year is not None else None,
                "format_type": str(artwork.format_type) if artwork.format_type is not None else None,
                "dimensions": str(artwork.dimensions) if artwork.dimensions is not None else None
            }
            artwork_id_int: int = artwork.id  # type: ignore
            vector_service.upsert_artwork_embedding(
                artwork_id_int,
                vector_embedding,
                metadata
            )
    
    db.commit()
    db.refresh(artwork)
    
    return artwork

@router.delete("/{artwork_id}")
async def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Delete artwork from catalog"""
    
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Delete from Pinecone if available
    if vector_service.is_available():
        vector_service.delete_artwork_embedding(artwork_id)
    
    # Delete from database
    db.delete(artwork)
    db.commit()
    
    return {"message": f"Artwork {artwork_id} deleted successfully"}

@router.post("/bulk-embed", response_model=BulkEmbedResponse, dependencies=[FastAPIDepends(verify_api_key)])
async def bulk_embed_artworks(
    request: BulkEmbedRequest,
    db: Session = Depends(get_db)
):
    """Generate embeddings for artwork catalog"""
    
    if not vector_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Vector service not available. Please check Pinecone configuration."
        )
    
    # Get artworks to process
    query = db.query(Artwork)
    
    if request.artwork_ids:
        # Process specific artworks
        query = query.filter(Artwork.id.in_(request.artwork_ids))
    else:
        # Process artworks without embeddings (unless force_regenerate is True)
        if not request.force_regenerate:
            query = query.filter(Artwork.vector_embedding.is_(None))
    
    artworks = query.all()
    
    processed_count = 0
    failed_count = 0
    failed_artwork_ids = []
    
    for artwork in artworks:
        try:
            # Generate embedding
            vector_embedding = get_artwork_embedding_by_title(str(artwork.title))
            if not vector_embedding:
                artwork_hash = hash(f"{artwork.title}{artwork.year}{artwork.format_type}")
                vector_embedding = generate_mock_embedding(abs(artwork_hash) % 10000)
            
            # Update database
            setattr(artwork, 'vector_embedding', vector_embedding)
            
            # Store in Pinecone
            metadata = {
                "title": str(artwork.title),
                "year": int(artwork.year) if artwork.year is not None else None,
                "format_type": str(artwork.format_type) if artwork.format_type is not None else None,
                "dimensions": str(artwork.dimensions) if artwork.dimensions is not None else None
            }
            
            artwork_id_val: int = artwork.id  # type: ignore
            success = vector_service.upsert_artwork_embedding(
                artwork_id_val,
                vector_embedding,
                metadata
            )
            
            if success:
                processed_count += 1
            else:
                failed_count += 1
                failed_artwork_ids.append(artwork.id)
                
        except Exception as e:
            print(f"Failed to process artwork {artwork.id}: {e}")
            failed_count += 1
            failed_artwork_ids.append(artwork.id)
    
    # Commit database changes
    db.commit()
    
    return BulkEmbedResponse(
        processed_count=processed_count,
        failed_count=failed_count,
        message=f"Processed {processed_count} artworks, {failed_count} failed",
        failed_artwork_ids=failed_artwork_ids if failed_artwork_ids else None
    )