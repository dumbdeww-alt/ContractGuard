from enum import Enum
from pydantic import BaseModel, Field


class ChangeSeverity(str, Enum):
    BREAKING = "BREAKING"
    NON_BREAKING = "NON_BREAKING"


class CompatibilityStatus(str, Enum):
    BREAKING = "BREAKING"
    NON_BREAKING = "NON_BREAKING"


class ChangeType(str, Enum):
    TYPE_CHANGED = "TYPE_CHANGED"
    REQUIRED_FIELD_REMOVED = "REQUIRED_FIELD_REMOVED"
    OPTIONAL_FIELD_REMOVED = "OPTIONAL_FIELD_REMOVED"
    REQUIRED_FIELD_ADDED = "REQUIRED_FIELD_ADDED"
    OPTIONAL_FIELD_ADDED = "OPTIONAL_FIELD_ADDED"
    FIELD_MADE_REQUIRED = "FIELD_MADE_REQUIRED"
    FIELD_MADE_OPTIONAL = "FIELD_MADE_OPTIONAL"
    FIELD_CONSTRAINT_STRICTER = "FIELD_CONSTRAINT_STRICTER"
    METADATA_CHANGED = "METADATA_CHANGED"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"


class SchemaChangeDetail(BaseModel):
    path: str = Field(..., description="Field path or property name in schema")
    change_type: ChangeType = Field(..., description="Machine-readable change identifier")
    old_value: str | None = Field(None, description="Previous value or type specification")
    new_value: str | None = Field(None, description="New value or type specification")
    severity: ChangeSeverity = Field(..., description="Severity classification: BREAKING or NON_BREAKING")
    reason: str = Field(..., description="Detailed explanation of the change and its downstream compatibility consequence")


class CompatibilityCheckRequest(BaseModel):
    old_version: int = Field(..., gt=0, description="Base contract version number to compare from")
    new_version: int = Field(..., gt=0, description="Target contract version number to compare to")


class CompatibilityReportResponse(BaseModel):
    contract_id: int = Field(..., description="ID of the contract evaluated")
    contract_name: str = Field(..., description="Name of the contract evaluated")
    old_version: int = Field(..., description="Base version number compared")
    new_version: int = Field(..., description="Target version number compared")
    compatible: bool = Field(..., description="True if no breaking changes were detected, False otherwise")
    status: CompatibilityStatus = Field(..., description="Overall compatibility status: BREAKING or NON_BREAKING")
    breaking_changes: int = Field(..., description="Total count of breaking changes detected")
    non_breaking_changes: int = Field(..., description="Total count of non-breaking changes detected")
    changes: list[SchemaChangeDetail] = Field(default_factory=list, description="List of all detected schema changes")
