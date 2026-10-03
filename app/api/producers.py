import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.producer import Producer
from app.schemas.producer import ProducerCreate, ProducerResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/producers", tags=["Producers"])


@router.post("", response_model=ProducerResponse, status_code=status.HTTP_201_CREATED)
def create_producer(payload: ProducerCreate, db: Session = Depends(get_db)) -> Producer:
    """Register a new data producer system."""
    existing = db.query(Producer).filter(Producer.name == payload.name).first()
    if existing:
        logger.warning("Conflict creating producer: name '%s' already exists", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Producer with name '{payload.name}' already exists.",
        )

    producer = Producer(name=payload.name, description=payload.description)
    try:
        db.add(producer)
        db.commit()
        db.refresh(producer)
        logger.info("Successfully registered producer id=%d name='%s'", producer.id, producer.name)
        return producer
    except IntegrityError:
        db.rollback()
        logger.warning("Integrity error registering producer name '%s'", payload.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Producer with name '{payload.name}' already exists.",
        )


@router.get("", response_model=list[ProducerResponse])
def list_producers(db: Session = Depends(get_db)) -> list[Producer]:
    """Retrieve all registered producer systems."""
    return db.query(Producer).order_by(Producer.id).all()


@router.get("/{id}", response_model=ProducerResponse)
def get_producer(id: int, db: Session = Depends(get_db)) -> Producer:
    """Retrieve a specific producer system by its unique ID."""
    producer = db.query(Producer).filter(Producer.id == id).first()
    if not producer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producer with ID {id} not found.",
        )
    return producer
