from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.consumer import ConsumerResponse
from app.schemas.contract_version import ContractVersionSummaryResponse
from app.schemas.producer import ProducerResponse


class ContractBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique name of the data contract")
    description: str | None = Field(None, description="Description of the contract purpose")


class ContractCreate(ContractBase):
    producer_id: int = Field(..., description="ID of the publishing producer system")
    consumer_ids: list[int] = Field(default_factory=list, description="IDs of consumer systems subscribing to this contract")


class ContractResponse(ContractBase):
    id: int
    producer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractDetailResponse(ContractResponse):
    producer: ProducerResponse
    consumers: list[ConsumerResponse] = Field(default_factory=list)
    versions: list[ContractVersionSummaryResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
