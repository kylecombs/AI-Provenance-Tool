from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from app.core.config import settings

# API Key authentication for POC
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key for authentication.
    In production, this should be more sophisticated with:
    - Database lookup for API keys
    - Rate limiting per key
    - Key expiration
    - Different permission levels
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Include X-API-Key header."
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return api_key

# Dependency to use in routes that require authentication
RequireAPIKey = Depends(verify_api_key)