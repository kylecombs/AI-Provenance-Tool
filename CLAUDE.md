# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a full-stack AI-powered artwork identification and provenance tracking system. The backend uses FastAPI with PostgreSQL for structured data and Pinecone for vector similarity search. The frontend is a React TypeScript application.

### Core Data Flow
1. **Artworks** are catalogued with 512-dimensional vector embeddings stored in both PostgreSQL and Pinecone
2. **Installation photos** from exhibitions are processed to detect artworks using AI/CV models
3. **Detections** with confidence scores and bounding boxes link photos to artworks  
4. **Provenance records** are automatically created, building exhibition history for each artwork
5. **Vector search** enables similarity matching across the artwork database

### Key Architectural Patterns
- **Service Layer Architecture**: Business logic separated into services/ (vector_service.py handles Pinecone)
- **Dual Storage**: Structured data in PostgreSQL, vector embeddings in Pinecone for performance
- **Background Processing**: Async image analysis with job tracking via processing API
- **Auto-Embedding**: Artworks automatically generate vector embeddings on create/update

## Development Commands

### Backend Development
```bash
# Quick start (recommended)
make dev                    # Start development server with auto-reload
./run_dev.sh [port]        # Shell script with automatic port conflict resolution
python run_dev.py --port 8001  # Cross-platform script with options

# Database management  
make migrate               # Run Alembic database migrations
make seed                 # Populate database with sample artworks and exhibitions
alembic revision --autogenerate -m "description"  # Create new migration

# Development utilities
make install              # Setup virtual environment and install dependencies
make clean               # Clean up Python cache and generated files
```

### Frontend Development
```bash
cd frontend/
npm start                # Development server on port 3000
npm run build           # Production build
npm test               # Run test suite
```

### Service Management
```bash
./manage-services.sh start    # Start PostgreSQL and Redis (macOS with Homebrew)
./manage-services.sh status   # Check service status
./manage-services.sh stop     # Stop all services
```

## Database Schema & Relationships

The schema implements a sophisticated provenance tracking system:

- **artworks** ← **detections** → **installation_photos** → **exhibitions**
- **provenance_records** links artworks to exhibitions via detections
- All foreign keys are indexed; confidence_score and processing status are indexed for queries
- Vector embeddings stored as ARRAY(Float) in PostgreSQL, synced to Pinecone index `artwork-embeddings`

Key relationship: One detection in an installation photo creates one provenance record, building the exhibition history chain.

## API Structure

### `/api/v1/artworks/` 
- CRUD operations with pagination, filtering by year/format_type  
- POST automatically generates vector embeddings and stores in Pinecone
- GET `/bulk-embeddings` for batch processing

### `/api/v1/process/`
- POST `/photos` submits installation photos for background AI analysis
- GET `/jobs/{job_id}` polls processing status
- Creates detections with confidence scores and bounding boxes

### `/api/v1/results/`
- GET `/similarity/{artwork_id}` uses Pinecone for vector similarity search
- PUT `/confirmations/{detection_id}` manual confirmation workflow
- GET `/provenance/{artwork_id}` complete exhibition history timeline

## Vector Search Integration

**Pinecone Configuration:**
- Index: `artwork-embeddings`, 512 dimensions, cosine similarity
- Metadata: artwork_id, title, year, format_type for filtering
- Service supports both Pinecone v2.x and v3.x clients (auto-detection)

**Key Methods in `vector_service.py`:**
- `upsert_artwork_embedding()` - Store/update vectors
- `search_similar_artworks()` - Find matches with confidence thresholds
- Automatic fallback to database similarity when Pinecone unavailable

## Environment Setup

**Required `.env` variables:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ai_provenance
PINECONE_API_KEY=your-pinecone-key
REDIS_URL=redis://localhost:6379  
API_KEY=your-api-key
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=["http://localhost:3000"]
```

**Development Dependencies:**
- Python 3.10+ (backend uses modern type hints and async/await)
- PostgreSQL 13+ and Redis for data storage
- Node.js 16+ for frontend React/TypeScript
- Pinecone account for vector search

## Testing & Quality

- **pytest** configured for backend API and service testing
- **Type checking** with SQLAlchemy models (use `# type: ignore` for Column descriptors)
- **Pydantic schemas** handle all request/response validation
- **Health checks** at `/health` with database connection status
- **Comprehensive logging** with request IDs for debugging

## Development Notes

**Port Conflict Handling:** All startup scripts automatically detect port conflicts and use alternatives (8001-8010)

**Mock AI Pipeline:** Current computer vision is mock implementation - replace `extract_image_features()` in `embedding_utils.py` with real CV models

**Error Handling:** Global middleware captures exceptions with structured responses; use custom exceptions in `schemas/errors.py`

**Database Migrations:** Always create migrations for schema changes; foreign key relationships are strictly enforced

**Vector Sync:** Changes to artwork embeddings automatically sync to Pinecone; monitor for consistency