# AI Provenance Tool - Backend

FastAPI backend for the AI-powered artwork identification and provenance tracking system.

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)

```bash
# For macOS/Linux
./run_dev.sh

# For Windows  
run_dev.bat

# Cross-platform Python script
python run_dev.py

# Using Make (if you have it installed)
make dev
```

### Option 2: Manual Setup

1. **Create virtual environment**: `python -m venv venv`
2. **Activate**: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Configure environment**: Copy `.env.example` to `.env` and fill in values
5. **Run migrations**: `alembic upgrade head`
6. **Seed database** (optional): `python app/utils/seed_data.py`
7. **Start server**: `uvicorn app.main:app --reload`

### Development Commands

```bash
# Different ways to start the server
./run_dev.sh [port]              # Shell script with custom port
python run_dev.py --port 8001    # Python script with options
make dev                         # Make command
make install                     # Install dependencies
make migrate                     # Run database migrations
make seed                        # Seed with sample data
make test                        # Run tests
make clean                       # Clean up files
```

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive Swagger UI

## 🗄️ Database Schema

The system uses PostgreSQL with the following core tables:

### Core Tables

#### `artworks`
Stores artwork metadata and vector embeddings for similarity search.
```sql
- id (Primary Key)
- title (String, indexed)
- year (Integer)
- format_type (String) -- painting, sculpture, photograph, etc.
- dimensions (String)
- image_url (Text)
- vector_embedding (Array of Float) -- 512-dimensional embedding
```

#### `exhibitions`
Exhibition information where artworks are displayed.
```sql
- id (Primary Key)
- name (String, indexed)
- venue (String)
- start_date (Date)
- end_date (Date)
```

#### `installation_photos`
Photos of exhibition installations to be processed for artwork detection.
```sql
- id (Primary Key)
- exhibition_id (Foreign Key -> exhibitions.id, indexed)
- photo_url (String)
- processed_status (Enum: pending, processing, completed, failed, indexed)
```

#### `detections`
AI-detected artworks within installation photos.
```sql
- id (Primary Key)
- installation_photo_id (Foreign Key -> installation_photos.id, indexed)
- artwork_id (Foreign Key -> artworks.id, indexed)
- confidence_score (Float, indexed)
- bounding_box (JSON) -- {x, y, width, height}
```

#### `provenance_records`
Links artworks to exhibitions through detections for provenance tracking.
```sql
- id (Primary Key)
- artwork_id (Foreign Key -> artworks.id, indexed)
- exhibition_id (Foreign Key -> exhibitions.id, indexed)
- detection_id (Foreign Key -> detections.id, indexed)
- created_at (DateTime, indexed, auto-generated)
```

### Relationships
- One artwork can have many detections (across different photos)
- One exhibition can have many installation photos
- One installation photo can have many detections
- One detection creates one provenance record

## 🔧 Services

### Vector Service (`app/services/vector_service.py`)
Manages artwork vector embeddings using Pinecone for similarity search.

**Key Methods:**
- `upsert_artwork_embedding()` - Store artwork embeddings
- `search_similar_artworks()` - Find similar artworks by embedding
- `get_artwork_embedding()` - Retrieve stored embedding
- `delete_artwork_embedding()` - Remove embedding
- `get_index_stats()` - Get Pinecone index statistics

**Configuration:**
- Index name: `artwork-embeddings`
- Dimension: 512 (configurable)
- Metric: cosine similarity
- Metadata: artwork_id, title, year, format_type

### Database Service (`app/core/database.py`)
SQLAlchemy configuration and session management.

**Usage:**
```python
from app.core.database import get_db

def some_api_endpoint(db: Session = Depends(get_db)):
    # Use db session here
    pass
```

## 🛠️ Utilities

### Embedding Utils (`app/utils/embedding_utils.py`)
Utilities for generating and working with artwork embeddings.

**Functions:**
- `generate_mock_embedding()` - Generate test embeddings
- `extract_image_features()` - Extract features from image URLs
- `calculate_similarity()` - Compute cosine similarity
- `get_artwork_embedding_by_title()` - Get pre-computed embeddings

### Data Seeding (`app/utils/seed_data.py`)
Populate database with sample data for testing and development.

**Usage:**
```bash
python app/utils/seed_data.py
```

**Creates:**
- 5 famous artworks with embeddings
- 3 sample exhibitions
- 4 installation photos
- 4 artwork detections
- 4 provenance records
- Stores embeddings in Pinecone (if configured)

## 🔄 Database Migrations

Using Alembic for database schema management.

**Commands:**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🌐 Environment Configuration

Required environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_provenance

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# API Configuration
API_PORT=8000
API_URL=http://localhost:8000

# Security
SECRET_KEY=your-secret-key
API_KEY=your-api-key

# AI Services
OPENAI_API_KEY=your-openai-key
GOOGLE_CLOUD_PROJECT_ID=your-project-id
AZURE_CUSTOM_VISION_KEY=your-azure-key

# Vector Search
PINECONE_API_KEY=your-pinecone-key

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Settings and configuration
│   │   └── database.py        # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── artwork.py
│   │   ├── exhibition.py
│   │   ├── installation_photo.py
│   │   ├── detection.py
│   │   └── provenance_record.py
│   ├── services/
│   │   └── vector_service.py  # Pinecone integration
│   ├── utils/
│   │   ├── seed_data.py       # Database seeding
│   │   └── embedding_utils.py # Embedding utilities
│   ├── api/                   # API endpoints (to be implemented)
│   ├── schemas/               # Pydantic schemas (to be implemented)
│   └── main.py               # FastAPI application
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔍 Performance Optimizations

- **Database Indexes**: All foreign keys and frequently queried fields are indexed
- **Vector Search**: Pinecone provides sub-100ms similarity search
- **Connection Pooling**: SQLAlchemy manages database connections
- **Async Support**: FastAPI enables async request handling

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📊 Monitoring

- Health check endpoint: `GET /health`
- API metrics available at: `GET /metrics` (to be implemented)
- Database connection status included in health checks