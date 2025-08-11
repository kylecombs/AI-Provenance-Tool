import numpy as np
from typing import List, Optional
from PIL import Image
import requests
from io import BytesIO

def generate_mock_embedding(artwork_id: int, dimension: int = 512) -> List[float]:
    """
    Generate a mock embedding vector for an artwork.
    In production, this would use a real image embedding model like CLIP or ResNet.
    
    Args:
        artwork_id: ID of the artwork to generate embedding for
        dimension: Dimension of the embedding vector
        
    Returns:
        List of floats representing the mock embedding
    """
    # Use artwork_id as seed for consistent embeddings
    np.random.seed(artwork_id)
    
    # Generate random normalized vector
    embedding = np.random.normal(0, 1, dimension)
    
    # L2 normalize the embedding
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding.tolist()

def extract_image_features(image_url: str) -> Optional[List[float]]:
    """
    Extract features from an image URL using a mock feature extractor.
    In production, this would use a pre-trained model like CLIP, ResNet, or similar.
    
    Args:
        image_url: URL of the image to process
        
    Returns:
        List of floats representing the image features, or None if extraction fails
    """
    try:
        # In a real implementation, you would:
        # 1. Download the image
        # 2. Preprocess it (resize, normalize, etc.)
        # 3. Run it through a pre-trained CNN or Vision Transformer
        # 4. Extract features from a specific layer
        
        # For now, return a mock embedding based on URL hash
        url_hash = hash(image_url)
        np.random.seed(abs(url_hash) % (2**31))
        
        embedding = np.random.normal(0, 1, 512)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()
        
    except Exception as e:
        print(f"Error extracting features from {image_url}: {e}")
        return None

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Cosine similarity score between -1 and 1
    """
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
        
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

# Example embeddings for famous artworks (these would be computed from actual images)
FAMOUS_ARTWORK_EMBEDDINGS = {
    "starry_night": generate_mock_embedding(1, 512),
    "persistence_of_memory": generate_mock_embedding(2, 512),
    "campbells_soup": generate_mock_embedding(3, 512),
    "girl_pearl_earring": generate_mock_embedding(4, 512),
    "the_thinker": generate_mock_embedding(5, 512),
}

def get_artwork_embedding_by_title(title: str) -> Optional[List[float]]:
    """Get a pre-computed embedding for a famous artwork by title"""
    title_normalized = title.lower().replace(" ", "_").replace("'", "")
    
    for key, embedding in FAMOUS_ARTWORK_EMBEDDINGS.items():
        if key in title_normalized or title_normalized in key:
            return embedding
    
    return None