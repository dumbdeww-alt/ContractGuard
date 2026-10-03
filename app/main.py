import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

import app.models

from app.api.consumers import router as consumers_router
from app.api.contracts import router as contracts_router
from app.api.health import router as health_router
from app.api.producers import router as producers_router
from app.api.approval import router as approval_router
from app.api.events import router as events_router

from app.config import get_settings
from app.database import Base, engine


logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="BIT-74 Data Contract Registry",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified successfully.")
except Exception as exc:
    logger.warning("Database initialization warning: %s", exc)


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError):
    logger.error("Database error: %s", exc)

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database service unavailable.",
            "error_code": "DATABASE_UNAVAILABLE",
        },
    )


app.include_router(health_router)
app.include_router(producers_router)
app.include_router(consumers_router)
app.include_router(contracts_router)
app.include_router(approval_router)
app.include_router(events_router)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/health",
        "contracts": "/contracts",
    }