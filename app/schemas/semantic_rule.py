from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class SemanticViolation(BaseModel):
    field: str = Field(..., description="The field in the data sample that violated the rule")
    rule: str = Field(..., description="The semantic rule expression that was violated")
    value: Any = Field(None, description="The actual value received in the data sample")
    message: str = Field(..., description="Explanation of the violation")


class SemanticValidationResponse(BaseModel):
    contract_id: int = Field(..., description="ID of the contract evaluated")
    contract_name: str = Field(..., description="Name of the contract evaluated")
    valid: bool = Field(..., description="True if all semantic rules passed, False if any failed")
    passed_rules: int = Field(..., description="Count of rules that passed")
    failed_rules: int = Field(..., description="Count of rules that failed")
    violations: list[SemanticViolation] = Field(default_factory=list, description="List of all rule violations")


class SemanticRuleResponse(BaseModel):
    id: int
    contract_id: int
    rule_name: str
    field_name: str
    rule_type: str
    rule_expression: str
    parameters: dict[str, Any]
    error_message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
