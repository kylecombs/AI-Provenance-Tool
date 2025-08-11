import sys
import os
from datetime import date, datetime
from typing import List

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.core.database import SessionLocal, engine
from app.models import (
    Artwork, Exhibition, InstallationPhoto, Detection, 
    ProvenanceRecord, ProcessedStatus, Base
)
from app.services.vector_service import vector_service
from app.utils.embedding_utils import generate_mock_embedding, get_artwork_embedding_by_title

def create_sample_artworks(db) -> List[Artwork]:
    """Create sample artworks with mock data"""
    artworks_data = [
        {
            "title": "Starry Night",
            "year": 1889,
            "format_type": "painting",
            "dimensions": "73.7 cm × 92.1 cm",
            "image_url": "https://example.com/images/starry_night.jpg",
            "vector_embedding": None  # Will be set after creation
        },
        {
            "title": "The Persistence of Memory",
            "year": 1931,
            "format_type": "painting", 
            "dimensions": "24 cm × 33 cm",
            "image_url": "https://example.com/images/persistence_memory.jpg",
            "vector_embedding": None  # Will be set after creation
        },
        {
            "title": "Campbell's Soup Cans",
            "year": 1962,
            "format_type": "silkscreen",
            "dimensions": "51 cm × 41 cm each",
            "image_url": "https://example.com/images/campbells_soup.jpg", 
            "vector_embedding": None  # Will be set after creation
        },
        {
            "title": "Girl with a Pearl Earring",
            "year": 1665,
            "format_type": "painting",
            "dimensions": "44.5 cm × 39 cm",
            "image_url": "https://example.com/images/girl_pearl_earring.jpg",
            "vector_embedding": None  # Will be set after creation
        },
        {
            "title": "The Thinker",
            "year": 1904,
            "format_type": "sculpture",
            "dimensions": "186 cm height",
            "image_url": "https://example.com/images/the_thinker.jpg",
            "vector_embedding": None  # Will be set after creation
        }
    ]
    
    artworks = []
    for i, artwork_data in enumerate(artworks_data):
        # Generate embedding for this artwork
        embedding = get_artwork_embedding_by_title(artwork_data["title"]) or generate_mock_embedding(i + 1)
        artwork_data["vector_embedding"] = embedding
        
        artwork = Artwork(**artwork_data)
        db.add(artwork)
        artworks.append(artwork)
    
    db.commit()
    # Refresh to get the IDs
    for artwork in artworks:
        db.refresh(artwork)
    
    # Store embeddings in Pinecone
    if vector_service.is_available():
        print("Storing embeddings in Pinecone...")
        for artwork in artworks:
            metadata = {
                "title": artwork.title,
                "year": artwork.year,
                "format_type": artwork.format_type,
                "dimensions": artwork.dimensions
            }
            vector_service.upsert_artwork_embedding(
                artwork.id, 
                artwork.vector_embedding,
                metadata
            )
    else:
        print("Pinecone not available, skipping vector storage")
    
    return artworks

def create_sample_exhibitions(db) -> List[Exhibition]:
    """Create sample exhibitions with mock data"""
    exhibitions_data = [
        {
            "name": "Masters of Modern Art",
            "venue": "Metropolitan Museum of Art",
            "start_date": date(2023, 3, 15),
            "end_date": date(2023, 8, 20)
        },
        {
            "name": "Contemporary Visions", 
            "venue": "Museum of Modern Art",
            "start_date": date(2023, 5, 1),
            "end_date": date(2023, 9, 15)
        },
        {
            "name": "European Classics",
            "venue": "Guggenheim Museum",
            "start_date": date(2023, 2, 10),
            "end_date": date(2023, 7, 30)
        }
    ]
    
    exhibitions = []
    for exhibition_data in exhibitions_data:
        exhibition = Exhibition(**exhibition_data)
        db.add(exhibition)
        exhibitions.append(exhibition)
    
    db.commit()
    # Refresh to get the IDs
    for exhibition in exhibitions:
        db.refresh(exhibition)
        
    return exhibitions

def create_sample_installation_photos(db, exhibitions: List[Exhibition]) -> List[InstallationPhoto]:
    """Create sample installation photos"""
    photos_data = [
        {
            "exhibition_id": exhibitions[0].id,
            "photo_url": "https://example.com/photos/met_gallery1.jpg",
            "processed_status": ProcessedStatus.COMPLETED
        },
        {
            "exhibition_id": exhibitions[0].id,
            "photo_url": "https://example.com/photos/met_gallery2.jpg", 
            "processed_status": ProcessedStatus.COMPLETED
        },
        {
            "exhibition_id": exhibitions[1].id,
            "photo_url": "https://example.com/photos/moma_main_hall.jpg",
            "processed_status": ProcessedStatus.COMPLETED
        },
        {
            "exhibition_id": exhibitions[2].id,
            "photo_url": "https://example.com/photos/guggenheim_spiral.jpg",
            "processed_status": ProcessedStatus.PROCESSING
        }
    ]
    
    photos = []
    for photo_data in photos_data:
        photo = InstallationPhoto(**photo_data)
        db.add(photo)
        photos.append(photo)
        
    db.commit()
    # Refresh to get the IDs
    for photo in photos:
        db.refresh(photo)
        
    return photos

def create_sample_detections(db, photos: List[InstallationPhoto], artworks: List[Artwork]) -> List[Detection]:
    """Create sample detections linking photos to artworks"""
    detections_data = [
        {
            "installation_photo_id": photos[0].id,
            "artwork_id": artworks[0].id,  # Starry Night
            "confidence_score": 0.95,
            "bounding_box": {"x": 100, "y": 50, "width": 300, "height": 400}
        },
        {
            "installation_photo_id": photos[0].id,
            "artwork_id": artworks[1].id,  # Persistence of Memory
            "confidence_score": 0.87,
            "bounding_box": {"x": 450, "y": 80, "width": 250, "height": 200}
        },
        {
            "installation_photo_id": photos[1].id,
            "artwork_id": artworks[2].id,  # Campbell's Soup Cans
            "confidence_score": 0.92,
            "bounding_box": {"x": 200, "y": 150, "width": 200, "height": 300}
        },
        {
            "installation_photo_id": photos[2].id,
            "artwork_id": artworks[3].id,  # Girl with Pearl Earring
            "confidence_score": 0.89,
            "bounding_box": {"x": 300, "y": 100, "width": 180, "height": 220}
        }
    ]
    
    detections = []
    for detection_data in detections_data:
        detection = Detection(**detection_data)
        db.add(detection)
        detections.append(detection)
        
    db.commit()
    # Refresh to get the IDs  
    for detection in detections:
        db.refresh(detection)
        
    return detections

def create_sample_provenance_records(db, artworks: List[Artwork], exhibitions: List[Exhibition], detections: List[Detection]):
    """Create sample provenance records"""
    provenance_data = [
        {
            "artwork_id": artworks[0].id,
            "exhibition_id": exhibitions[0].id,
            "detection_id": detections[0].id
        },
        {
            "artwork_id": artworks[1].id,
            "exhibition_id": exhibitions[0].id,
            "detection_id": detections[1].id
        },
        {
            "artwork_id": artworks[2].id,
            "exhibition_id": exhibitions[0].id,
            "detection_id": detections[2].id
        },
        {
            "artwork_id": artworks[3].id,
            "exhibition_id": exhibitions[1].id,
            "detection_id": detections[3].id
        }
    ]
    
    for record_data in provenance_data:
        record = ProvenanceRecord(**record_data)
        db.add(record)
        
    db.commit()

def seed_database():
    """Main function to seed the database with sample data"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        print("Creating sample artworks...")
        artworks = create_sample_artworks(db)
        print(f"Created {len(artworks)} artworks")
        
        print("Creating sample exhibitions...")
        exhibitions = create_sample_exhibitions(db)
        print(f"Created {len(exhibitions)} exhibitions")
        
        print("Creating sample installation photos...")
        photos = create_sample_installation_photos(db, exhibitions)
        print(f"Created {len(photos)} installation photos")
        
        print("Creating sample detections...")
        detections = create_sample_detections(db, photos, artworks)
        print(f"Created {len(detections)} detections")
        
        print("Creating sample provenance records...")
        create_sample_provenance_records(db, artworks, exhibitions, detections)
        print("Created provenance records")
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()