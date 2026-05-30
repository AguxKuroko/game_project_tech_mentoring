import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.api_keys_config import api_game_key

logger = logging.getLogger(__name__)

backend_key_header = APIKeyHeader(name="X-BACKEND-KEY", auto_error=False)


def verify_backend_api_key(backend_api_key: str | None = Security(backend_key_header)) -> str:
    """Verify the X-BACKEND-KEY header. Returns a status message on success."""
    if backend_api_key is None or backend_api_key != api_game_key.BACKEND_API_KEY:
        logger.warning("Auth failed: invalid or missing X-BACKEND-KEY header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    logger.debug("Auth succeeded for X-BACKEND-KEY")
    return "Authorization successful"
