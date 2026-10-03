import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.consumer import Consumer
from app.schemas.consumer import ConsumerCreate, ConsumerResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consumers", tags=["Consumers"])


@router.post("", response_model=ConsumerResponse, status_code=status.HTTP_201_CREATED)
def create_consumer(payload: ConsumerCreate, db: Session = Depends(get_db)) -> Consumer:
    """Register a new downstream data consumer system."""
    existing = db.query(Consumer).filter(Consumer.name == payload.name).first()
    if existing:
        logger.warning("Conflict creating consumer: name '%s' already exists", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Consumer with name '{payload.name}' already exists.",
        )

    consumer = Consumer(name=payload.name, description=payload.description)
    try:
        db.add(consumer)
        db.commit()
        db.refresh(consumer)
        logger.info("Successfully registered consumer id=%d name='%s'", consumer.id, consumer.name)
        return consumer
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error registering consumer name '%s'", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Consumer with name '{payload.name}' already exists.",
        )


@router.get("", response_model=list[ConsumerResponse])
def list_consumers(db: Session = Depends(get_db)) -> list[Consumer]:
    """Retrieve all registered consumer systems."""
    return db.query(Consumer).order_by(Consumer.id).all()


@router.get("/{id}", response_model=ConsumerResponse)
def get_consumer(id: int, db: Session = Depends(get_db)) -> Consumer:
    """Retrieve a specific consumer system by its unique ID."""
    consumer = db.query(Consumer).filter(Consumer.id == id).first()
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumer with ID {id} not found.",
        )
    return consumer
