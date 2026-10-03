"""Impact Analysis Pydantic schemas for Contract Guard."""
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.compatibility import CompatibilityStatus, SchemaChangeDetail


class ImpactStatus(str, Enum):
    """Impact severity classification for contract evolution."""

    HIGH = "HIGH"
    NONE = "NONE"


class AffectedConsumer(BaseModel):
    """Summary of a consumer system affected by contract evolution."""

    id: int = Field(..., description="ID of the affected consumer system")
    name: str = Field(..., description="Name of the affected consumer system")

    model_config = ConfigDict(from_attributes=True)


class ImpactAnalysisRequest(BaseModel):
    """Request payload for evaluating downstream impact between two versions."""

    old_version: int = Field(..., gt=0, description="Base contract version number to compare from")
    new_version: int = Field(..., gt=0, description="Target contract version number to compare to")


class ImpactAnalysisResponse(BaseModel):
    """Comprehensive impact analysis report combining compatibility and lineage."""

    contract_id: int = Field(..., description="ID of the evaluated contract")
    contract_name: str = Field(..., description="Name of the evaluated contract")
    old_version: int = Field(..., description="Base version number compared")
    new_version: int = Field(..., description="Target version number compared")
    compatibility_status: CompatibilityStatus = Field(
        ..., description="Compatibility status from schema comparison: BREAKING or NON_BREAKING"
    )
    compatible: bool = Field(..., description="True if no breaking changes were detected, False otherwise")
    breaking_changes: int = Field(..., description="Total count of breaking changes detected")
    non_breaking_changes: int = Field(..., description="Total count of non-breaking changes detected")
    impact_status: ImpactStatus = Field(
        ..., description="Overall downstream impact classification: HIGH if breaking changes exist, NONE otherwise"
    )
    affected_consumer_count: int = Field(..., description="Number of downstream consumers potentially affected")
    affected_consumers: list[AffectedConsumer] = Field(
        default_factory=list, description="Downstream consumer systems affected by breaking changes"
    )
    changes: list[SchemaChangeDetail] = Field(
        default_factory=list, description="Detailed list of schema changes detected between versions"
    )

    model_config = ConfigDict(from_attributes=True)
