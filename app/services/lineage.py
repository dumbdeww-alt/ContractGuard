"""Lineage Service for Contract Guard.

Provides domain capabilities to answer:
"Who produces this contract, and which systems consume it?"
Contract Lineage Model: Producer -> Contract -> Consumers
"""

from sqlalchemy.orm import Session, joinedload

from app.models.contract import Contract
from app.schemas.lineage import (
    ContractLineageResponse,
    LineageConsumer,
    LineageProducer,
)


class LineageService:
    """Core domain service for inspecting contract lineage relationships."""

    @classmethod
    def get_contract_lineage(
        cls, db: Session, contract_id: int
    ) -> ContractLineageResponse | None:
        """Retrieve the lineage graph for a given contract ID.

        Returns ContractLineageResponse representing Producer -> Contract -> Consumers,
        or None if the contract does not exist.
        """
        contract = (
            db.query(Contract)
            .options(
                joinedload(Contract.producer),
                joinedload(Contract.consumers),
            )
            .filter(Contract.id == contract_id)
            .first()
        )
        if not contract:
            return None

        # Sort consumers deterministically by id
        sorted_consumers = sorted(contract.consumers, key=lambda c: c.id)

        return ContractLineageResponse(
            contract_id=contract.id,
            contract_name=contract.name,
            producer=LineageProducer(
                id=contract.producer.id,
                name=contract.producer.name,
            ),
            consumers=[
                LineageConsumer(id=consumer.id, name=consumer.name)
                for consumer in sorted_consumers
            ],
        )
