from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProducerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the producer system")
    description: str | None = Field(None, description="Description of the producer system")


class ProducerCreate(ProducerBase):
    pass


class ProducerResponse(ProducerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
