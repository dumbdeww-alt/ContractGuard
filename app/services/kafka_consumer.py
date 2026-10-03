"""Kafka Consumer Service for Contract Guard.

Consumes streaming events from Apache Kafka and routes them to Phase 8
RuntimeValidationService for two-tier JSON Schema and semantic validation.
"""

import json
import logging
from typing import Any
from confluent_kafka import Consumer, KafkaError, KafkaException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.kafka_event import KafkaEventEnvelope
from app.schemas.runtime_validation import RuntimeValidationResponse
from app.services.runtime_validator import (
    ContractNotFoundError,
    RuntimeValidationService,
    VersionNotFoundError,
)

logger = logging.getLogger(__name__)


class KafkaConsumerError(Exception):
    """Raised when consuming from Kafka encounters an unrecoverable error."""
    pass


class KafkaConsumerService:
    """Service for consuming, deserializing, and validating streaming contract events."""

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        topic: str | None = None,
        group_id: str | None = None,
        auto_offset_reset: str = "earliest",
        consumer_instance: Any = None,
    ) -> None:
        settings = get_settings()
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.topic = topic or settings.kafka_topic
        self.group_id = group_id or settings.kafka_consumer_group
        self.auto_offset_reset = auto_offset_reset
        self._consumer = consumer_instance

    @property
    def consumer(self) -> Any:
        """Lazy-initialize or return the underlying Kafka consumer."""
        if self._consumer is None:
            config = {
                "bootstrap.servers": self.bootstrap_servers,
                "group.id": self.group_id,
                "auto.offset.reset": self.auto_offset_reset,
                "enable.auto.commit": False,  # Manual offset commitment
            }
            self._consumer = Consumer(config)
            self._consumer.subscribe([self.topic])
            logger.info(
                "Subscribed Kafka consumer to topic '%s' with group '%s'",
                self.topic,
                self.group_id,
            )
        return self._consumer

    def process_raw_message(
        self,
        raw_payload: str | bytes,
        db: Session,
    ) -> dict[str, Any]:
        """Deserialize and validate a single Kafka message payload using Phase 8 validation.

        This method is transport-decoupled and directly testable.

        Args:
            raw_payload: Raw JSON string or UTF-8 bytes from Kafka.
            db: Active SQLAlchemy Session.

        Returns:
            Dict containing processing status, event_id, valid flag, and validation details.
        """
        # 1. JSON Deserialization
        if isinstance(raw_payload, bytes):
            try:
                raw_payload = raw_payload.decode("utf-8")
            except UnicodeDecodeError as exc:
                logger.error("Failed to decode message bytes as UTF-8: %s", exc)
                return {
                    "status": "ERROR",
                    "error_type": "DECODE_ERROR",
                    "message": f"Malformed UTF-8 payload: {exc}",
                }

        try:
            data = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            logger.error("Failed to deserialize JSON message: %s", exc)
            return {
                "status": "ERROR",
                "error_type": "MALFORMED_JSON",
                "message": f"Malformed JSON: {exc.msg}",
            }

        # 2. Event Envelope Validation
        try:
            envelope = KafkaEventEnvelope.model_validate(data)
        except ValidationError as exc:
            logger.error("Event envelope schema violation: %s", exc.errors())
            return {
                "status": "ERROR",
                "error_type": "INVALID_ENVELOPE",
                "message": f"Invalid event envelope: {exc.error_count()} validation error(s)",
                "errors": exc.errors(),
            }

        event_id = envelope.event_id
        contract_id = envelope.contract_id
        version_number = envelope.version
        sample = envelope.payload

        # 3. Phase 8 Runtime Validation Execution
        try:
            validation_response: RuntimeValidationResponse = (
                RuntimeValidationService.validate_runtime_sample(
                    db=db,
                    contract_id=contract_id,
                    version_number=version_number,
                    sample=sample,
                )
            )
        except ContractNotFoundError as exc:
            logger.error(
                "Event %s validation failed: Contract ID %d not found in registry",
                event_id,
                contract_id,
            )
            return {
                "status": "ERROR",
                "event_id": event_id,
                "error_type": "CONTRACT_NOT_FOUND",
                "message": str(exc),
            }
        except VersionNotFoundError as exc:
            logger.error(
                "Event %s validation failed: Version %d for Contract ID %d not found in registry",
                event_id,
                version_number,
                contract_id,
            )
            return {
                "status": "ERROR",
                "event_id": event_id,
                "error_type": "VERSION_NOT_FOUND",
                "message": str(exc),
            }
        except Exception as exc:
            logger.error(
                "Unexpected error during validation for event %s: %s",
                event_id,
                exc,
                exc_info=True,
            )
            return {
                "status": "ERROR",
                "event_id": event_id,
                "error_type": "VALIDATION_EXCEPTION",
                "message": str(exc),
            }

        # 4. Structured Logging of Results
        if validation_response.valid:
            logger.info(
                "VALID event received: event_id='%s', contract_id=%d, version=%d",
                event_id,
                contract_id,
                version_number,
            )
        else:
            schema_err_count = validation_response.schema_validation.error_count
            semantic_err_count = validation_response.semantic_validation.failed_rules
            logger.warning(
                "INVALID event received: event_id='%s', contract_id=%d, version=%d (schema_errors=%d, semantic_failures=%d)",
                event_id,
                contract_id,
                version_number,
                schema_err_count,
                semantic_err_count,
            )

        return {
            "status": "SUCCESS",
            "event_id": event_id,
            "contract_id": contract_id,
            "version": version_number,
            "valid": validation_response.valid,
            "validation_response": validation_response,
        }

    def consume_message(self, db: Session, timeout: float = 1.0) -> dict[str, Any] | None:
        """Poll the consumer for a single message, process it, and commit offset on success."""
        msg = self.consumer.poll(timeout)
        if msg is None:
            return None

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.debug(
                    "Reached end of partition %s [%d] at offset %d",
                    msg.topic(),
                    msg.partition(),
                    msg.offset(),
                )
                return None
            logger.error("Kafka consumer error: %s", msg.error())
            raise KafkaConsumerError(f"Kafka consumer error: {msg.error()}")

        try:
            result = self.process_raw_message(raw_payload=msg.value(), db=db)
            self.consumer.commit(message=msg, asynchronous=False)
            return result
        except Exception as exc:
            logger.error("Error processing Kafka message at offset %d: %s", msg.offset(), exc)
            self.consumer.commit(message=msg, asynchronous=False)
            return {
                "status": "ERROR",
                "error_type": "PROCESSING_EXCEPTION",
                "message": str(exc),
            }

    def close(self) -> None:
        """Close the Kafka consumer gracefully."""
        if self._consumer is not None:
            try:
                self._consumer.close()
                logger.info("Kafka consumer closed successfully.")
            except Exception as exc:
                logger.warning("Error closing Kafka consumer: %s", exc)
