from .artwork import (
    ArtworkBase,
    ArtworkCreate,
    ArtworkUpdate,
    ArtworkResponse,
    ArtworkListResponse,
    BulkEmbedRequest,
    BulkEmbedResponse
)

from .exhibition import (
    ExhibitionBase,
    ExhibitionCreate,
    ExhibitionUpdate,
    ExhibitionResponse,
    ExhibitionListResponse
)

from .processing import (
    ProcessingStatus,
    ProcessInstallationPhotoRequest,
    ProcessInstallationPhotoResponse,
    ProcessingStatusResponse,
    BoundingBox,
    DetectionResponse,
    PhotoDetectionsResponse
)

from .results import (
    SimilarArtwork,
    MatchesResponse,
    ConfirmMatchRequest,
    ConfirmMatchResponse,
    ProvenanceEntry,
    ProvenanceResponse,
    ProvenanceExportRequest,
    ProvenanceExportResponse
)

__all__ = [
    # Artwork schemas
    "ArtworkBase",
    "ArtworkCreate", 
    "ArtworkUpdate",
    "ArtworkResponse",
    "ArtworkListResponse",
    "BulkEmbedRequest",
    "BulkEmbedResponse",
    
    # Exhibition schemas
    "ExhibitionBase",
    "ExhibitionCreate",
    "ExhibitionUpdate", 
    "ExhibitionResponse",
    "ExhibitionListResponse",
    
    # Processing schemas
    "ProcessingStatus",
    "ProcessInstallationPhotoRequest",
    "ProcessInstallationPhotoResponse",
    "ProcessingStatusResponse",
    "BoundingBox",
    "DetectionResponse",
    "PhotoDetectionsResponse",
    
    # Results schemas
    "SimilarArtwork",
    "MatchesResponse",
    "ConfirmMatchRequest",
    "ConfirmMatchResponse",
    "ProvenanceEntry",
    "ProvenanceResponse",
    "ProvenanceExportRequest",
    "ProvenanceExportResponse"
]