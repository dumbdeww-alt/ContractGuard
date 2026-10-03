from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ConsumerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the consumer system")
    description: str | None = Field(None, description="Description of the consumer system")


class ConsumerCreate(ConsumerBase):
    pass


class ConsumerResponse(ConsumerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
