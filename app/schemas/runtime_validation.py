"""Pydantic schemas for Phase 8 Runtime Sample Validation.

Validates live runtime data samples against both JSON Schema (structural tier)
and semantic business rules (semantic tier).
"""

from pydantic import BaseModel, Field

from app.schemas.semantic_rule import SemanticValidationResponse


class SchemaViolation(BaseModel):
    """Detailed information about an individual JSON Schema violation."""

    field: str = Field(
        ...,
        description="The field path in the data sample where the schema violation occurred",
    )
    keyword: str = Field(
        ...,
        description="The JSON Schema validation keyword violated (e.g., 'type', 'required')",
    )
    message: str = Field(
        ...,
        description="Human-readable explanation of the schema violation",
    )


class SchemaValidationResult(BaseModel):
    """Result of validating data sample against the contract version's JSON Schema."""

    valid: bool = Field(
        ...,
        description="True if data sample adheres strictly to JSON Schema, False otherwise",
    )
    error_count: int = Field(
        ...,
        description="Number of JSON Schema errors detected",
    )
    errors: list[SchemaViolation] = Field(
        default_factory=list,
        description="List of all detected JSON Schema violations",
    )


class RuntimeValidationResponse(BaseModel):
    """Comprehensive runtime validation report separating schema and semantic findings."""

    contract_id: int = Field(
        ...,
        description="ID of the contract evaluated",
    )
    contract_name: str = Field(
        ...,
        description="Name of the contract evaluated",
    )
    version_number: int = Field(
        ...,
        description="Contract schema version against which the sample was validated",
    )
    valid: bool = Field(
        ...,
        description="True only if BOTH JSON Schema and semantic rules validations pass",
    )
    schema_validation: SchemaValidationResult = Field(
        ...,
        description="Findings from JSON Schema structural evaluation",
    )
    semantic_validation: SemanticValidationResponse = Field(
        ...,
        description="Findings from semantic business rules evaluation",
    )
