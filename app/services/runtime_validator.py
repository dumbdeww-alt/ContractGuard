"""Runtime Sample Validation Service for Contract Guard.

Executes two-tier validation on live data samples:
1. Structural validation against the contract version's JSON Schema.
2. Business logic validation against all semantic rules configured for the contract.
"""

import re
from typing import Any
import jsonschema
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.semantic_rule import SemanticRule
from app.schemas.runtime_validation import (
    RuntimeValidationResponse,
    SchemaValidationResult,
    SchemaViolation,
)
from app.services.semantic_validator import SemanticValidationEngine


class RuntimeValidationError(Exception):
    """Base exception for runtime validation errors."""
    pass


class ContractNotFoundError(RuntimeValidationError):
    """Raised when the target contract is not found."""
    pass


class VersionNotFoundError(RuntimeValidationError):
    """Raised when the target contract version is not found."""
    pass


class RuntimeValidationService:
    """Core domain service for runtime sample validation."""

    @staticmethod
    def _extract_field_path(err: jsonschema.ValidationError) -> str:
        """Extract a readable field path from a jsonschema ValidationError."""
        if err.validator == "required":
            match = re.search(r"'([^']+)' is a required property", err.message)
            if match:
                prop = match.group(1)
                if err.path:
                    return f"{'.'.join(str(p) for p in err.path)}.{prop}"
                return prop
        if err.path:
            return ".".join(str(p) for p in err.path)
        return "$"

    @classmethod
    def validate_runtime_sample(
        cls,
        db: Session,
        contract_id: int,
        version_number: int,
        sample: dict[str, Any],
    ) -> RuntimeValidationResponse:
        """Validate a data sample against a specific contract version's schema and semantic rules.

        Raises:
            ContractNotFoundError: If the contract ID does not exist.
            VersionNotFoundError: If the version number does not exist for the contract.
        """
        # 1. Retrieve contract
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise ContractNotFoundError(f"Contract with ID {contract_id} not found.")

        # 2. Retrieve contract version
        contract_version = (
            db.query(ContractVersion)
            .filter(
                ContractVersion.contract_id == contract_id,
                ContractVersion.version_number == version_number,
            )
            .first()
        )
        if not contract_version:
            raise VersionNotFoundError(
                f"Version {version_number} not found for contract ID {contract_id}."
            )

        # 3. JSON Schema validation
        schema_definition = contract_version.schema_definition
        validator_cls = jsonschema.validators.validator_for(schema_definition)
        validator = validator_cls(schema_definition)

        schema_errors: list[SchemaViolation] = []
        raw_errors = sorted(
            validator.iter_errors(sample),
            key=lambda e: (str(list(e.path)), e.message),
        )

        for err in raw_errors:
            field = cls._extract_field_path(err)
            schema_errors.append(
                SchemaViolation(
                    field=field,
                    keyword=str(err.validator or "validation"),
                    message=err.message,
                )
            )

        schema_valid = len(schema_errors) == 0
        schema_result = SchemaValidationResult(
            valid=schema_valid,
            error_count=len(schema_errors),
            errors=schema_errors,
        )

        # 4. Semantic rules validation
        semantic_rules = (
            db.query(SemanticRule)
            .filter(SemanticRule.contract_id == contract_id)
            .order_by(SemanticRule.id)
            .all()
        )
        semantic_result = SemanticValidationEngine.validate_sample(
            rules=semantic_rules,
            sample=sample,
            contract_id=contract.id,
            contract_name=contract.name,
        )

        # 5. Composite validation result (True only if BOTH pass)
        overall_valid = schema_result.valid and semantic_result.valid

        return RuntimeValidationResponse(
            contract_id=contract.id,
            contract_name=contract.name,
            version_number=version_number,
            valid=overall_valid,
            schema_validation=schema_result,
            semantic_validation=semantic_result,
        )
