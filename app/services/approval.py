"""Approval Workflow and Audit Trail Service for Contract Guard.

Manages approval requests, state transitions, dynamic compatibility and impact calculations,
and atomic audit logging.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.approval_request import ApprovalRequest
from app.models.audit_event import AuditEvent
from app.models.contract import Contract
from app.schemas.approval import (
    ApprovalRequestResponse,
    ApprovalStatus,
)
from app.schemas.audit import AuditAction, AuditEventResponse
from app.schemas.compatibility import CompatibilityReportResponse
from app.services.impact_analysis import ImpactAnalysisService


class ApprovalWorkflowError(Exception):
    """Base exception for approval workflow errors."""
    pass


class ApprovalRequestNotFoundError(ApprovalWorkflowError):
    """Raised when an approval request ID is not found."""
    pass


class InvalidStateTransitionError(ApprovalWorkflowError):
    """Raised when an invalid status transition is attempted."""
    pass


class ApprovalService:
    """Core domain service for managing contract evolution approvals and audit trails."""

    @classmethod
    def _enrich_approval_request(
        cls, db: Session, req: ApprovalRequest
    ) -> ApprovalRequestResponse:
        """Enrich ApprovalRequest entity with dynamic compatibility, impact, and audit history."""
        # 1. Resolve contract name
        contract_name = req.contract.name if req.contract else ""
        if not contract_name:
            contract = db.query(Contract).filter(Contract.id == req.contract_id).first()
            contract_name = contract.name if contract else ""

        # 2. Dynamically calculate impact & compatibility via ImpactAnalysisService
        try:
            impact = ImpactAnalysisService.analyze_impact(
                db=db,
                contract_id=req.contract_id,
                old_version=req.old_version,
                new_version=req.new_version,
            )
            compatibility = CompatibilityReportResponse(
                contract_id=impact.contract_id,
                contract_name=impact.contract_name,
                old_version=impact.old_version,
                new_version=impact.new_version,
                compatible=impact.compatible,
                status=impact.compatibility_status,
                breaking_changes=impact.breaking_changes,
                non_breaking_changes=impact.non_breaking_changes,
                changes=impact.changes,
            )
        except Exception:
            impact = None
            compatibility = None

        # 3. Retrieve audit events in chronological order
        audit_events = (
            db.query(AuditEvent)
            .filter(AuditEvent.approval_request_id == req.id)
            .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
            .all()
        )

        return ApprovalRequestResponse(
            id=req.id,
            contract_id=req.contract_id,
            contract_name=contract_name,
            old_version=req.old_version,
            new_version=req.new_version,
            status=ApprovalStatus(req.status),
            requested_by=req.requested_by,
            approver=req.approver,
            reason=req.reason,
            created_at=req.created_at,
            decided_at=req.decided_at,
            compatibility=compatibility,
            impact=impact,
            audit_events=[
                AuditEventResponse.model_validate(event) for event in audit_events
            ],
        )

    @classmethod
    def create_approval_request(
        cls,
        db: Session,
        contract_id: int,
        old_version: int,
        new_version: int,
        requested_by: str,
    ) -> ApprovalRequestResponse:
        """Create a new approval request and its initial audit event in a single transaction."""
        # 1. Verify contract and versions exist by running ImpactAnalysisService first.
        # This will raise SameVersionError (400), ContractNotFoundError (404), or VersionNotFoundError (404).
        ImpactAnalysisService.analyze_impact(
            db=db,
            contract_id=contract_id,
            old_version=old_version,
            new_version=new_version,
        )

        # 2. Persist approval request and audit event atomically
        try:
            req = ApprovalRequest(
                contract_id=contract_id,
                old_version=old_version,
                new_version=new_version,
                status=ApprovalStatus.PENDING.value,
                requested_by=requested_by,
                created_at=datetime.now(timezone.utc),
            )
            db.add(req)
            db.flush()

            audit_event = AuditEvent(
                approval_request_id=req.id,
                action=AuditAction.APPROVAL_REQUEST_CREATED.value,
                actor=requested_by,
                details=f"Approval request created for version {old_version} -> {new_version}.",
                created_at=datetime.now(timezone.utc),
            )
            db.add(audit_event)
            db.commit()
            db.refresh(req)
        except Exception:
            db.rollback()
            raise

        return cls._enrich_approval_request(db, req)

    @classmethod
    def approve_request(
        cls,
        db: Session,
        request_id: int,
        approver: str,
        reason: str | None = None,
    ) -> ApprovalRequestResponse:
        """Approve a pending approval request and record an APPROVAL_REQUEST_APPROVED audit event."""
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not req:
            raise ApprovalRequestNotFoundError(
                f"Approval request with ID {request_id} not found."
            )

        if req.status == ApprovalStatus.APPROVED.value:
            raise InvalidStateTransitionError("Cannot approve an already approved request.")
        if req.status == ApprovalStatus.REJECTED.value:
            raise InvalidStateTransitionError("Cannot approve an already rejected request.")

        try:
            now = datetime.now(timezone.utc)
            req.status = ApprovalStatus.APPROVED.value
            req.approver = approver
            req.reason = reason
            req.decided_at = now

            audit_event = AuditEvent(
                approval_request_id=req.id,
                action=AuditAction.APPROVAL_REQUEST_APPROVED.value,
                actor=approver,
                details=reason or "Approval request approved.",
                created_at=now,
            )
            db.add(audit_event)
            db.commit()
            db.refresh(req)
        except Exception:
            db.rollback()
            raise

        return cls._enrich_approval_request(db, req)

    @classmethod
    def reject_request(
        cls,
        db: Session,
        request_id: int,
        approver: str,
        reason: str | None = None,
    ) -> ApprovalRequestResponse:
        """Reject a pending approval request and record an APPROVAL_REQUEST_REJECTED audit event."""
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not req:
            raise ApprovalRequestNotFoundError(
                f"Approval request with ID {request_id} not found."
            )

        if req.status == ApprovalStatus.REJECTED.value:
            raise InvalidStateTransitionError("Cannot reject an already rejected request.")
        if req.status == ApprovalStatus.APPROVED.value:
            raise InvalidStateTransitionError("Cannot reject an already approved request.")

        try:
            now = datetime.now(timezone.utc)
            req.status = ApprovalStatus.REJECTED.value
            req.approver = approver
            req.reason = reason
            req.decided_at = now

            audit_event = AuditEvent(
                approval_request_id=req.id,
                action=AuditAction.APPROVAL_REQUEST_REJECTED.value,
                actor=approver,
                details=reason or "Approval request rejected.",
                created_at=now,
            )
            db.add(audit_event)
            db.commit()
            db.refresh(req)
        except Exception:
            db.rollback()
            raise

        return cls._enrich_approval_request(db, req)

    @classmethod
    def get_approval_request(
        cls,
        db: Session,
        request_id: int,
    ) -> ApprovalRequestResponse:
        """Retrieve full details of a specific approval request."""
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not req:
            raise ApprovalRequestNotFoundError(
                f"Approval request with ID {request_id} not found."
            )
        return cls._enrich_approval_request(db, req)

    @classmethod
    def list_approval_requests(
        cls,
        db: Session,
        status: ApprovalStatus | None = None,
    ) -> list[ApprovalRequestResponse]:
        """List all approval requests in deterministic order (newest first)."""
        query = db.query(ApprovalRequest)
        if status:
            query = query.filter(ApprovalRequest.status == status.value)
        requests = query.order_by(
            ApprovalRequest.created_at.desc(),
            ApprovalRequest.id.desc(),
        ).all()
        return [cls._enrich_approval_request(db, req) for req in requests]

    @classmethod
    def get_audit_history(
        cls,
        db: Session,
        request_id: int,
    ) -> list[AuditEventResponse]:
        """Retrieve the chronological audit trail for a specific approval request."""
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if not req:
            raise ApprovalRequestNotFoundError(
                f"Approval request with ID {request_id} not found."
            )

        events = (
            db.query(AuditEvent)
            .filter(AuditEvent.approval_request_id == request_id)
            .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
            .all()
        )
        return [AuditEventResponse.model_validate(e) for e in events]
