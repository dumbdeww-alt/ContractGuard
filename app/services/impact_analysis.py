"""Impact Analysis Service for Contract Guard.

Combines schema compatibility evaluation (Phase 3) and data lineage (Phase 5)
to calculate downstream consumer impact of contract evolution.
"""

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.schemas.impact_analysis import (
    AffectedConsumer,
    ImpactAnalysisResponse,
    ImpactStatus,
)
from app.services.compatibility import CompatibilityEngine
from app.services.lineage import LineageService


class ImpactAnalysisError(Exception):
    """Base exception for impact analysis errors."""
    pass


class ContractNotFoundError(ImpactAnalysisError):
    """Raised when the target contract is not found."""
    pass


class VersionNotFoundError(ImpactAnalysisError):
    """Raised when a requested contract version is not found."""
    pass


class SameVersionError(ImpactAnalysisError):
    """Raised when old_version and new_version are identical."""
    pass


class ImpactAnalysisService:
    """Core domain service for calculating downstream consumer impact of schema changes."""

    @classmethod
    def analyze_impact(
        cls,
        db: Session,
        contract_id: int,
        old_version: int,
        new_version: int,
    ) -> ImpactAnalysisResponse:
        """Analyze downstream consumer impact caused by evolving a contract schema.

        Pipeline:
        1. Validate distinct versions.
        2. Retrieve contract and both version definitions from database.
        3. Run CompatibilityEngine to identify breaking/non-breaking changes.
        4. Retrieve contract downstream consumers via LineageService.
        5. Apply MVP Impact Policy:
           - breaking_changes > 0 -> HIGH impact, all downstream consumers affected.
           - breaking_changes == 0 -> NONE impact, zero consumers affected.
        6. Return structured ImpactAnalysisResponse.
        """
        # 1. Distinct version validation
        if old_version == new_version:
            raise SameVersionError(
                "old_version and new_version must be distinct version numbers."
            )

        # 2. Retrieve contract
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise ContractNotFoundError(f"Contract with ID {contract_id} not found.")

        # 3. Retrieve old and new version records
        v_old = (
            db.query(ContractVersion)
            .filter(
                ContractVersion.contract_id == contract_id,
                ContractVersion.version_number == old_version,
            )
            .first()
        )
        if not v_old:
            raise VersionNotFoundError(
                f"Version {old_version} not found for contract ID {contract_id}."
            )

        v_new = (
            db.query(ContractVersion)
            .filter(
                ContractVersion.contract_id == contract_id,
                ContractVersion.version_number == new_version,
            )
            .first()
        )
        if not v_new:
            raise VersionNotFoundError(
                f"Version {new_version} not found for contract ID {contract_id}."
            )

        # 4. Evaluate schema compatibility via CompatibilityEngine
        compat_report = CompatibilityEngine.compare_schemas(
            old_schema=v_old.schema_definition,
            new_schema=v_new.schema_definition,
            old_version=old_version,
            new_version=new_version,
            contract_id=contract.id,
            contract_name=contract.name,
        )

        # 5. Determine downstream consumers via LineageService
        lineage = LineageService.get_contract_lineage(db=db, contract_id=contract_id)
        downstream_consumers = lineage.consumers if lineage else []

        # 6. Apply MVP Impact Policy
        if compat_report.breaking_changes > 0:
            impact_status = ImpactStatus.HIGH
            affected_consumers = [
                AffectedConsumer(id=c.id, name=c.name) for c in downstream_consumers
            ]
        else:
            impact_status = ImpactStatus.NONE
            affected_consumers = []

        # 7. Construct and return structured impact report
        return ImpactAnalysisResponse(
            contract_id=contract.id,
            contract_name=contract.name,
            old_version=old_version,
            new_version=new_version,
            compatibility_status=compat_report.status,
            compatible=compat_report.compatible,
            breaking_changes=compat_report.breaking_changes,
            non_breaking_changes=compat_report.non_breaking_changes,
            impact_status=impact_status,
            affected_consumer_count=len(affected_consumers),
            affected_consumers=affected_consumers,
            changes=compat_report.changes,
        )
