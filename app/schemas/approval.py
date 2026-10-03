"""Approval schemas for Contract Guard."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.audit import AuditEventResponse
from app.schemas.compatibility import CompatibilityReportResponse
from app.schemas.impact_analysis import ImpactAnalysisResponse


class ApprovalStatus(str, Enum):
    """Approval status enumeration."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalRequestCreate(BaseModel):
    """Payload to create an approval request for contract schema evolution."""

    contract_id: int = Field(..., gt=0, description="Target contract ID")
    old_version: int = Field(..., gt=0, description="Base version number to compare from")
    new_version: int = Field(..., gt=0, description="Proposed version number to compare to")
    requested_by: str = Field(..., min_length=1, max_length=255, description="Name or identifier of requester")


class ApprovalDecisionRequest(BaseModel):
    """Payload to approve or reject an approval request."""

    approver: str = Field(..., min_length=1, max_length=255, description="Name or identifier of decider")
    reason: str | None = Field(None, max_length=1000, description="Reason or comments for decision")


class ApprovalRequestResponse(BaseModel):
    """Approval request response containing metadata, dynamic compatibility, and impact."""

    id: int = Field(..., description="Unique approval request ID")
    contract_id: int = Field(..., description="Target contract ID")
    contract_name: str = Field(..., description="Target contract name")
    old_version: int = Field(..., description="Base version number")
    new_version: int = Field(..., description="Proposed version number")
    status: ApprovalStatus = Field(..., description="Current status: PENDING, APPROVED, or REJECTED")
    requested_by: str = Field(..., description="Name or identifier of requester")
    approver: str | None = Field(None, description="Name or identifier of decider if decided")
    reason: str | None = Field(None, description="Reason or comments for decision")
    created_at: datetime = Field(..., description="Timestamp when the request was submitted")
    decided_at: datetime | None = Field(None, description="Timestamp when the decision was made")
    compatibility: CompatibilityReportResponse | None = Field(
        None, description="Dynamically calculated schema compatibility report"
    )
    impact: ImpactAnalysisResponse | None = Field(
        None, description="Dynamically calculated downstream consumer impact report"
    )
    audit_events: list[AuditEventResponse] = Field(
        default_factory=list, description="Chronological audit trail of actions on this request"
    )

    model_config = ConfigDict(from_attributes=True)
