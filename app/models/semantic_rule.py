from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class SemanticRule(Base):
    __tablename__ = "semantic_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_name = Column(String(255), nullable=False)
    field_name = Column(String(255), nullable=False, index=True)
    rule_type = Column(String(50), nullable=False)
    rule_expression = Column(String(255), nullable=False)
    parameters = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    error_message = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("contract_id", "rule_name", name="uq_contract_rule_name"),
    )

    contract = relationship("Contract", back_populates="semantic_rules")
