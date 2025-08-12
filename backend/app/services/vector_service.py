import os
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from app.core.config import settings

try:
    # Try new Pinecone client first (v3.0+)
    from pinecone import Pinecone
    pinecone_client = None
    PINECONE_V3 = True
except ImportError:
    try:
        # Fall back to old Pinecone client (v2.x)
        import pinecone
        pinecone_client = pinecone
        PINECONE_V3 = False
    except ImportError:
        pinecone_client = None
        PINECONE_V3 = False

class VectorService:
    """Service for managing artwork vector embeddings with Pinecone"""
    
    def __init__(self):
        self.index: Optional[Any] = None
        self.index_name: str = "artwork-embeddings"
        self.dimension: int = 512  # Typical dimension for image embeddings
        self.metric: str = "cosine"
        self._initialize_pinecone()
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client and index"""
        if not pinecone_client and not PINECONE_V3:
            print("Warning: Pinecone client not installed. Vector operations will be disabled.")
            return
            
        if not settings.PINECONE_API_KEY:
            print("Warning: PINECONE_API_KEY not set. Vector operations will be disabled.")
            return
        
        try:
            if PINECONE_V3:
                # New Pinecone client (v3.0+)
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                
                # List existing indexes
                existing_indexes = [index.name for index in pc.list_indexes()]  # type: ignore
                
                # Create index if it doesn't exist
                if self.index_name not in existing_indexes:
                    print(f"Creating Pinecone index '{self.index_name}'...")
                    pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric=self.metric,
                        spec={
                            "serverless": {
                                "cloud": "aws",
                                "region": "us-east-1"
                            }
                        }
                    )  # type: ignore
                
                # Connect to the index
                self.index = pc.Index(self.index_name)  # type: ignore
                print(f"Connected to Pinecone index '{self.index_name}' (v3.0+)")
                
            else:
                # Old Pinecone client (v2.x)
                pinecone_client.init(  # type: ignore
                    api_key=settings.PINECONE_API_KEY,
                    environment="us-east1-gcp"  # Default environment, should be configurable
                )
                
                # Create index if it doesn't exist
                if self.index_name not in pinecone_client.list_indexes():  # type: ignore
                    print(f"Creating Pinecone index '{self.index_name}'...")
                    pinecone_client.create_index(  # type: ignore
                        name=self.index_name,
                        dimension=self.dimension,
                        metric=self.metric,
                        metadata_config={
                            "indexed": ["artwork_id", "title", "year", "format_type"]
                        }
                    )
                
                # Connect to the index
                self.index = pinecone_client.Index(self.index_name)  # type: ignore
                print(f"Connected to Pinecone index '{self.index_name}' (v2.x)")
            
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
        metadata: Optional[Dict[str, Any]] = None
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
            self.index.upsert(vectors=[vector_data])  # type: ignore
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
        filter_metadata: Optional[Dict[str, Any]] = None
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
            if self.index is None:
                print("Vector service index not initialized")
                return []
                
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata  # type: ignore
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
            fetch_response = self.index.fetch(ids=[str(artwork_id)])  # type: ignore
            
            if str(artwork_id) in fetch_response.vectors:
                vector_data = fetch_response.vectors[str(artwork_id)]
                return vector_data.values  # type: ignore
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
            self.index.delete(ids=[str(artwork_id)])  # type: ignore
            print(f"Successfully deleted embedding for artwork {artwork_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting embedding for artwork {artwork_id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        if not self.is_available():
            return {"error": "Vector service not available"}
        
        try:
            stats = self.index.describe_index_stats()  # type: ignore
            return {
                "total_vector_count": getattr(stats, 'total_vector_count', 0),
                "dimension": getattr(stats, 'dimension', self.dimension),
                "index_fullness": getattr(stats, 'index_fullness', 0.0),
                "namespaces": dict(getattr(stats, 'namespaces', {})) if hasattr(stats, 'namespaces') else {}
            }
        except Exception as e:
            return {"error": f"Failed to get index stats: {e}"}

# Global instance
vector_service = VectorService()