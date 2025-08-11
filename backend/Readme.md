# backend/README.md
# AI Provenance Tool - Backend

## Setup

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in values
5. Run migrations: `alembic upgrade head`
6. Start server: `uvicorn app.main:app --reload`

## API Documentation

Once running, visit http://localhost:8000/docs for Swagger UI