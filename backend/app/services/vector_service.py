import os
import numpy as np
from typing import List, Dict, Optional, Tuple
from app.core.config import settings

try:
    import pinecone
except ImportError:
    pinecone = None

class VectorService:
    """Service for managing artwork vector embeddings with Pinecone"""
    
    def __init__(self):
        self.index = None
        self.index_name = "artwork-embeddings"
        self.dimension = 512  # Typical dimension for image embeddings
        self.metric = "cosine"
        self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        if not pinecone:
            print("Warning: Pinecone client not installed. Vector operations will be disabled.")
            return
            
        if not settings.PINECONE_API_KEY:
            print("Warning: PINECONE_API_KEY not set. Vector operations will be disabled.")
            return
        
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment="us-east1-gcp"  # Default environment, should be configurable
            )
            
            # Create index if it doesn't exist
            if self.index_name not in pinecone.list_indexes():
                print(f"Creating Pinecone index '{self.index_name}'...")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    metadata_config={
                        "indexed": ["artwork_id", "title", "year", "format_type"]
                    }
                )
            
            # Connect to the index
            self.index = pinecone.Index(self.index_name)
            print(f"Connected to Pinecone index '{self.index_name}'")
            
        except Exception as e:
            print(f"Failed to initialize Pinecone: {e}")
            self.index = None
    
    def is_available(self) -> bool:
        """Check if vector service is available"""
        return self.index is not None
    
    def upsert_artwork_embedding(
        self,
        artwork_id: int,
        embedding: List[float],
        metadata: Dict = None
    ) -> bool:
        """
        Store or update an artwork's vector embedding in Pinecone
        
        Args:
            artwork_id: Database ID of the artwork
            embedding: Vector embedding as list of floats
            metadata: Additional metadata to store (title, year, etc.)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available():
            print("Vector service not available")
            return False
        
        try:
            # Prepare the vector data
            vector_data = {
                "id": str(artwork_id),
                "values": embedding,
                "metadata": metadata or {}
            }
            
            # Upsert to Pinecone
            self.index.upsert(vectors=[vector_data])
            print(f"Successfully stored embedding for artwork {artwork_id}")
            return True
            
        except Exception as e:
            print(f"Error storing embedding for artwork {artwork_id}: {e}")
            return False
    
    def search_similar_artworks(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        filter_metadata: Dict = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar artworks using vector similarity
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            score_threshold: Minimum similarity score threshold
            filter_metadata: Metadata filters to apply
        
        Returns:
            List of tuples (artwork_id, similarity_score, metadata)
        """
        if not self.is_available():
            print("Vector service not available")
            return []
        
        try:
            # Perform similarity search
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            # Filter results by threshold and format response
            results = []
            for match in query_response.matches:
                if match.score >= score_threshold:
                    results.append((
                        match.id,
                        match.score, 
                        match.metadata
                    ))
            
            print(f"Found {len(results)} similar artworks above threshold {score_threshold}")
            return results
            
        except Exception as e:
            print(f"Error searching similar artworks: {e}")
            return []
    
    def get_artwork_embedding(self, artwork_id: int) -> Optional[List[float]]:
        """
        Retrieve an artwork's embedding from Pinecone
        
        Args:
            artwork_id: Database ID of the artwork
            
        Returns:
            List of floats representing the embedding, or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            # Fetch the vector
            fetch_response = self.index.fetch(ids=[str(artwork_id)])
            
            if str(artwork_id) in fetch_response.vectors:
                vector_data = fetch_response.vectors[str(artwork_id)]
                return vector_data.values
            else:
                print(f"No embedding found for artwork {artwork_id}")
                return None
                
        except Exception as e:
            print(f"Error retrieving embedding for artwork {artwork_id}: {e}")
            return None
    
    def delete_artwork_embedding(self, artwork_id: int) -> bool:
        """
        Delete an artwork's embedding from Pinecone
        
        Args:
            artwork_id: Database ID of the artwork
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.index.delete(ids=[str(artwork_id)])
            print(f"Successfully deleted embedding for artwork {artwork_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting embedding for artwork {artwork_id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the Pinecone index"""
        if not self.is_available():
            return {"error": "Vector service not available"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
        except Exception as e:
            return {"error": f"Failed to get index stats: {e}"}

# Global instance
vector_service = VectorService()