"""API router for Contract Guard approval requests and audit trails."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.approval import (
    ApprovalDecisionRequest,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalStatus,
)
from app.schemas.audit import AuditEventResponse
from app.services.approval import (
    ApprovalRequestNotFoundError,
    ApprovalService,
    InvalidStateTransitionError,
)
from app.services.impact_analysis import (
    ContractNotFoundError,
    SameVersionError,
    VersionNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/approval-requests", tags=["Approval Workflow"])


@router.post(
    "",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an approval request for contract schema evolution",
)
def create_approval_request(
    payload: ApprovalRequestCreate,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    """Submit an approval request for proposing a contract version evolution.

    Dynamically calculates compatibility and downstream impact and logs the
    APPROVAL_REQUEST_CREATED audit event in the same transaction.
    """
    try:
        resp = ApprovalService.create_approval_request(
            db=db,
            contract_id=payload.contract_id,
            old_version=payload.old_version,
            new_version=payload.new_version,
            requested_by=payload.requested_by,
        )
        logger.info(
            "Created approval request id=%d for contract id=%d (v%d -> v%d) by '%s'",
            resp.id,
            payload.contract_id,
            payload.old_version,
            payload.new_version,
            payload.requested_by,
        )
        return resp
    except SameVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except (ContractNotFoundError, VersionNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.post(
    "/{id}/approve",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a pending approval request",
)
def approve_request(
    id: int,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    """Approve a pending approval request and record an audit event."""
    try:
        resp = ApprovalService.approve_request(
            db=db,
            request_id=id,
            approver=payload.approver,
            reason=payload.reason,
        )
        logger.info("Approved approval request id=%d by approver '%s'", id, payload.approver)
        return resp
    except ApprovalRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidStateTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{id}/reject",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a pending approval request",
)
def reject_request(
    id: int,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    """Reject a pending approval request and record an audit event."""
    try:
        resp = ApprovalService.reject_request(
            db=db,
            request_id=id,
            approver=payload.approver,
            reason=payload.reason,
        )
        logger.info("Rejected approval request id=%d by approver '%s'", id, payload.approver)
        return resp
    except ApprovalRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except InvalidStateTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[ApprovalRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="List approval requests",
)
def list_approval_requests(
    status: ApprovalStatus | None = Query(None, description="Optional status filter"),
    db: Session = Depends(get_db),
) -> list[ApprovalRequestResponse]:
    """Retrieve all approval requests in deterministic order (newest first)."""
    return ApprovalService.list_approval_requests(db=db, status=status)


@router.get(
    "/{id}",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific approval request",
)
def get_approval_request(
    id: int,
    db: Session = Depends(get_db),
) -> ApprovalRequestResponse:
    """Retrieve an approval request with dynamic compatibility, impact, and audit history."""
    try:
        return ApprovalService.get_approval_request(db=db, request_id=id)
    except ApprovalRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/{id}/audit",
    response_model=list[AuditEventResponse],
    status_code=status.HTTP_200_OK,
    summary="Get audit history for an approval request",
)
def get_audit_history(
    id: int,
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    """Retrieve all audit events for an approval request in chronological order."""
    try:
        return ApprovalService.get_audit_history(db=db, request_id=id)
    except ApprovalRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
