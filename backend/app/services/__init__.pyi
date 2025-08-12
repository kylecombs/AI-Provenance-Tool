# Type stubs for services module

from typing import Any, Dict, List, Optional, Tuple

class VectorService:
    index: Optional[Any]
    index_name: str
    dimension: int
    metric: str
    
    def __init__(self) -> None: ...
    def _initialize_pinecone(self) -> None: ...
    def is_available(self) -> bool: ...
    def upsert_artwork_embedding(
        self,
        artwork_id: int,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool: ...
    def search_similar_artworks(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]: ...
    def get_artwork_embedding(self, artwork_id: int) -> Optional[List[float]]: ...
    def delete_artwork_embedding(self, artwork_id: int) -> bool: ...
    def get_index_stats(self) -> Dict[str, Any]: ...

vector_service: VectorService