"""Semantic Validation Engine Service.

Evaluates data payloads against semantic/business rules associated with a contract.
"""

from typing import Any

from app.models.semantic_rule import SemanticRule
from app.schemas.semantic_rule import (
    SemanticValidationResponse,
    SemanticViolation,
)


class SemanticValidationEngine:
    """Core domain service for evaluating semantic rules on data samples."""

    @classmethod
    def evaluate_rule(cls, rule: SemanticRule, sample: dict[str, Any]) -> SemanticViolation | None:
        """Evaluate a single semantic rule against a data sample.

        Returns a SemanticViolation if the rule fails, or None if it passes.
        """
        field_name = rule.field_name
        rule_type = rule.rule_type.upper()
        params = rule.parameters or {}

        # 1. Check if the field is present in the sample
        if field_name not in sample:
            return SemanticViolation(
                field=field_name,
                rule=rule.rule_expression,
                value=None,
                message=f"Required field '{field_name}' is missing from data sample",
            )

        value = sample[field_name]

        # 2. Evaluate based on rule type
        if rule_type == "MIN_VALUE":
            min_val = params.get("min")
            if min_val is not None:
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    return SemanticViolation(
                        field=field_name,
                        rule=rule.rule_expression,
                        value=value,
                        message=f"{field_name} must be a numeric value",
                    )
                if value < min_val:
                    return SemanticViolation(
                        field=field_name,
                        rule=rule.rule_expression,
                        value=value,
                        message=rule.error_message,
                    )

        elif rule_type == "MAX_VALUE":
            max_val = params.get("max")
            if max_val is not None:
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    return SemanticViolation(
                        field=field_name,
                        rule=rule.rule_expression,
                        value=value,
                        message=f"{field_name} must be a numeric value",
                    )
                if value > max_val:
                    return SemanticViolation(
                        field=field_name,
                        rule=rule.rule_expression,
                        value=value,
                        message=rule.error_message,
                    )

        elif rule_type == "ALLOWED_VALUES":
            allowed = params.get("allowed_values", [])
            if value not in allowed:
                return SemanticViolation(
                    field=field_name,
                    rule=rule.rule_expression,
                    value=value,
                    message=rule.error_message,
                )

        return None

    @classmethod
    def validate_sample(
        cls,
        rules: list[SemanticRule],
        sample: dict[str, Any],
        contract_id: int,
        contract_name: str,
    ) -> SemanticValidationResponse:
        """Validate a data sample against all semantic rules configured for the contract."""
        violations: list[SemanticViolation] = []
        passed_count = 0

        for rule in rules:
            violation = cls.evaluate_rule(rule, sample)
            if violation:
                violations.append(violation)
            else:
                passed_count += 1

        failed_count = len(violations)
        is_valid = failed_count == 0

        return SemanticValidationResponse(
            contract_id=contract_id,
            contract_name=contract_name,
            valid=is_valid,
            passed_rules=passed_count,
            failed_rules=failed_count,
            violations=violations,
        )
