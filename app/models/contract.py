from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.contract_consumer import contract_consumers


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    producer_id = Column(
        Integer,
        ForeignKey("producers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    producer = relationship("Producer", back_populates="contracts")
    consumers = relationship(
        "Consumer",
        secondary=contract_consumers,
        back_populates="contracts",
    )
    versions = relationship(
        "ContractVersion",
        back_populates="contract",
        cascade="all, delete-orphan",
        order_by="ContractVersion.version_number",
    )
    semantic_rules = relationship(
        "SemanticRule",
        back_populates="contract",
        cascade="all, delete-orphan",
        order_by="SemanticRule.id",
    )
    approval_requests = relationship(
        "ApprovalRequest",
        back_populates="contract",
    )

