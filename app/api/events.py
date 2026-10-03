import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.kafka_event import KafkaEventEnvelope, PublishEventResponse
from app.services.kafka_producer import KafkaProducerError, KafkaProducerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/publish",
    response_model=PublishEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish an event envelope to the configured Kafka topic",
)
def publish_event(payload: KafkaEventEnvelope) -> PublishEventResponse:
    """Publish a streaming data contract event to Apache Kafka.

    Validates the event envelope (event_id, contract_id, version, payload),
    serializes the envelope to JSON, and publishes it using the event_id as the message key.

    Note:
        Does NOT perform contract validation here. Validation is executed
        downstream by the Contract Guard Kafka consumer service.
    """
    logger.info(
        "Received event publish request: event_id='%s', contract_id=%d, version=%d",
        payload.event_id,
        payload.contract_id,
        payload.version,
    )
    producer_service = KafkaProducerService()
    try:
        result = producer_service.publish_event(event=payload)
        return PublishEventResponse(
            event_id=result["event_id"],
            topic=result["topic"],
            status=result["status"],
            message=result["message"],
        )
    except KafkaProducerError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to publish event to Kafka broker: {exc}",
        )
