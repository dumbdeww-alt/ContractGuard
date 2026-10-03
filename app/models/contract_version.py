from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number = Column(Integer, nullable=False)
    schema_definition = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("contract_id", "version_number", name="uq_contract_version"),
        CheckConstraint("version_number > 0", name="chk_positive_version_number"),
    )

    contract = relationship("Contract", back_populates="versions")
