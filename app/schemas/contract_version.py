from datetime import datetime
from typing import Any
import jsonschema
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContractVersionBase(BaseModel):
    version_number: int = Field(..., gt=0, description="Version sequence number (must be a positive integer)")
    schema_definition: dict[str, Any] = Field(..., description="Valid JSON Schema specification")
    description: str | None = Field(None, description="Optional release notes or description for this version")

    @field_validator("schema_definition")
    @classmethod
    def validate_schema(cls, v: Any) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("schema_definition must be a JSON object")
        if not v:
            raise ValueError("schema_definition cannot be an empty dictionary")
        try:
            validator_cls = jsonschema.validators.validator_for(v)
            validator_cls.check_schema(v)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Malformed JSON Schema: {e.message}")
        except Exception as e:
            raise ValueError(f"Invalid JSON Schema structure: {str(e)}")
        return v


class ContractVersionCreate(ContractVersionBase):
    pass


class ContractVersionResponse(ContractVersionBase):
    id: int
    contract_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractVersionSummaryResponse(BaseModel):
    id: int
    contract_id: int
    version_number: int
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
