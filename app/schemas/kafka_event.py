"""Pydantic schemas for Kafka event streaming.

Defines the event envelope structure for streaming runtime messages across
producers, Kafka topics, and the Contract Guard consumer.
"""

from typing import Any
from pydantic import BaseModel, Field


class KafkaEventEnvelope(BaseModel):
    """Standardized event envelope for data contract streaming."""

    event_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for this event instance (used as Kafka message key)",
    )
    contract_id: int = Field(
        ...,
        gt=0,
        description="Positive integer identifier of the contract governing this event",
    )
    version: int = Field(
        ...,
        gt=0,
        description="Schema version number against which this payload should be evaluated",
    )
    payload: dict[str, Any] = Field(
        ...,
        description="The actual runtime data payload to be validated",
    )


class PublishEventResponse(BaseModel):
    """Response returned after publishing an event to a Kafka topic."""

    event_id: str = Field(
        ...,
        description="Identifier of the published event",
    )
    topic: str = Field(
        ...,
        description="Kafka topic name to which the event was published",
    )
    status: str = Field(
        default="PUBLISHED",
        description="Publication outcome status",
    )
    message: str = Field(
        ...,
        description="Descriptive confirmation message",
    )
