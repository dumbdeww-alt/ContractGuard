"""SQLAlchemy model for Contract Guard audit events."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    approval_request_id = Column(
        Integer,
        ForeignKey("approval_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(String(50), nullable=False, index=True)
    actor = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    approval_request = relationship("ApprovalRequest", back_populates="audit_events")
