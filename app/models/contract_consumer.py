from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base

contract_consumers = Table(
    "contract_consumers",
    Base.metadata,
    Column("contract_id", Integer, ForeignKey("contracts.id", ondelete="CASCADE"), primary_key=True),
    Column("consumer_id", Integer, ForeignKey("consumers.id", ondelete="CASCADE"), primary_key=True),
)
