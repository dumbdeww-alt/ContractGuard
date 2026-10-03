"""SQLAlchemy model for Contract Guard approval requests."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    old_version = Column(Integer, nullable=False)
    new_version = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    requested_by = Column(String(255), nullable=False)
    approver = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    decided_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    contract = relationship("Contract", back_populates="approval_requests")
    audit_events = relationship(
        "AuditEvent",
        back_populates="approval_request",
        cascade="all, delete-orphan",
        order_by="AuditEvent.created_at, AuditEvent.id",
    )
