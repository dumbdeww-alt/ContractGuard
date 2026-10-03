"""Kafka Producer Service for Contract Guard.

Serializes and publishes event envelopes to Apache Kafka topics.
"""

import logging
from typing import Any
from confluent_kafka import KafkaError, KafkaException, Producer

from app.config import get_settings
from app.schemas.kafka_event import KafkaEventEnvelope

logger = logging.getLogger(__name__)


class KafkaProducerError(Exception):
    """Raised when publishing to Kafka encounters an error."""
    pass


class KafkaProducerService:
    """Service for serializing and publishing events to Apache Kafka."""

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        default_topic: str | None = None,
        producer_instance: Any = None,
    ) -> None:
        settings = get_settings()
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.default_topic = default_topic or settings.kafka_topic
        self._producer = producer_instance

    @property
    def producer(self) -> Any:
        """Lazy-initialize or return the underlying Kafka producer."""
        if self._producer is None:
            config = {
                "bootstrap.servers": self.bootstrap_servers,
                "client.id": "contract-guard-producer",
            }
            self._producer = Producer(config)
        return self._producer

    def publish_event(
        self,
        event: KafkaEventEnvelope,
        topic: str | None = None,
    ) -> dict[str, str]:
        """Serialize and produce an event envelope to Kafka.

        Args:
            event: Validated KafkaEventEnvelope instance.
            topic: Optional override destination topic.

        Returns:
            Dict containing publication status and metadata.

        Raises:
            KafkaProducerError: If the message cannot be queued or delivered.
        """
        target_topic = topic or self.default_topic
        key = event.event_id
        value_json = event.model_dump_json()

        delivery_error: KafkaError | None = None

        def delivery_report(err: KafkaError | None, msg: Any) -> None:
            nonlocal delivery_error
            if err is not None:
                delivery_error = err
                logger.error(
                    "Failed to deliver Kafka event %s to topic %s: %s",
                    key,
                    target_topic,
                    err,
                )
            else:
                logger.info(
                    "Delivered Kafka event %s to topic %s [partition %s] at offset %s",
                    key,
                    msg.topic(),
                    msg.partition(),
                    msg.offset(),
                )

        try:
            self.producer.produce(
                topic=target_topic,
                key=key.encode("utf-8"),
                value=value_json.encode("utf-8"),
                callback=delivery_report,
            )
            # Poll / flush to guarantee synchronous delivery for demo/HTTP producer path
            self.producer.poll(0)
            self.producer.flush(timeout=10.0)

            if delivery_error is not None:
                raise KafkaProducerError(f"Kafka delivery failed: {delivery_error}")

            logger.info("Successfully published event %s to topic %s", key, target_topic)
            return {
                "event_id": key,
                "topic": target_topic,
                "status": "PUBLISHED",
                "message": f"Event {key} successfully published to topic {target_topic}",
            }
        except KafkaProducerError:
            raise
        except (KafkaException, Exception) as exc:
            logger.error("Exception publishing event %s to Kafka: %s", key, exc)
            raise KafkaProducerError(f"Failed to publish event to Kafka: {exc}") from exc
