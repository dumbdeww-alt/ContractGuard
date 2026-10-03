"""Audit schemas for Contract Guard."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class AuditAction(str, Enum):
    """Audit action event types."""

    APPROVAL_REQUEST_CREATED = "APPROVAL_REQUEST_CREATED"
    APPROVAL_REQUEST_APPROVED = "APPROVAL_REQUEST_APPROVED"
    APPROVAL_REQUEST_REJECTED = "APPROVAL_REQUEST_REJECTED"


class AuditEventResponse(BaseModel):
    """Audit event log entry."""

    id: int = Field(..., description="Unique audit event ID")
    approval_request_id: int = Field(..., description="ID of the related approval request")
    action: str = Field(..., description="Action taken, e.g. APPROVAL_REQUEST_CREATED")
    actor: str = Field(..., description="User or system entity that performed the action")
    details: str | None = Field(None, description="Optional description or reason for the action")
    created_at: datetime = Field(..., description="Timestamp when the audit event occurred")

    model_config = ConfigDict(from_attributes=True)
