import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Service health and database connectivity check",
    responses={
        200: {
            "description": "Service and database healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "database": "connected"}
                }
            },
        },
        503: {
            "description": "Database connectivity failure",
            "content": {
                "application/json": {
                    "example": {"status": "unhealthy", "database": "disconnected"}
                }
            },
        },
    },
)
def get_health(db: Session = Depends(get_db)) -> JSONResponse:
    """Health check endpoint indicating service availability and database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "database": "connected"},
        )
    except Exception as exc:
        logger.error("Health check database probe failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"},
        )

