"""Lineage Pydantic schemas for Contract Guard."""
from pydantic import BaseModel, ConfigDict, Field


class LineageProducer(BaseModel):
    """Producer system summary in a contract lineage response."""

    id: int = Field(..., description="ID of the producer system")
    name: str = Field(..., description="Name of the producer system")

    model_config = ConfigDict(from_attributes=True)


class LineageConsumer(BaseModel):
    """Consumer system summary in a contract lineage response."""

    id: int = Field(..., description="ID of the consumer system")
    name: str = Field(..., description="Name of the consumer system")

    model_config = ConfigDict(from_attributes=True)


class ContractLineageResponse(BaseModel):
    """Response model representing the contract producer and consumers lineage graph."""

    contract_id: int = Field(..., description="ID of the data contract")
    contract_name: str = Field(..., description="Name of the data contract")
    producer: LineageProducer = Field(..., description="System that produces this contract")
    consumers: list[LineageConsumer] = Field(
        default_factory=list,
        description="Systems that consume this contract",
    )

    model_config = ConfigDict(from_attributes=True)
