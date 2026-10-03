"""Seed script for Contract Guard demonstration data in the simulated railway ecosystem.

This script populates:
- 2 Producers
- 3 Consumers
- 2 Contracts
  - Train Schedule Contract (v1 & v2)
  - Train Running Status Contract (v1)

Safe and idempotent: Can be executed multiple times without generating duplicate records.
"""

from typing import Any
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models.consumer import Consumer
from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.producer import Producer
from app.models.semantic_rule import SemanticRule

TRAIN_SCHEDULE_V1_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrainSchedule",
    "type": "object",
    "required": [
        "train_number",
        "train_name",
        "station_code",
        "arrival_time",
        "departure_time",
        "platform",
        "status",
    ],
    "properties": {
        "train_number": {
            "type": "string",
            "description": "Unique train identification number (e.g. 12951)",
        },
        "train_name": {
            "type": "string",
            "description": "Express or passenger train designation",
        },
        "station_code": {
            "type": "string",
            "description": "Station code abbreviation (e.g. BVI)",
        },
        "arrival_time": {
            "type": "string",
            "description": "Scheduled arrival time HH:MM",
        },
        "departure_time": {
            "type": "string",
            "description": "Scheduled departure time HH:MM",
        },
        "platform": {
            "type": "integer",
            "description": "Platform number (e.g. 4)",
        },
        "status": {
            "type": "string",
            "description": "Current schedule status (e.g. ON_TIME)",
        },
    },
    "additionalProperties": False,
}

TRAIN_SCHEDULE_V2_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrainSchedule",
    "type": "object",
    "required": [
        "train_number",
        "train_name",
        "station_code",
        "arrival_time",
        "departure_time",
        "platform",
        "status",
    ],
    "properties": {
        "train_number": {
            "type": "string",
            "description": "Unique train identification number (e.g. 12951)",
        },
        "train_name": {
            "type": "string",
            "description": "Express or passenger train designation",
        },
        "station_code": {
            "type": "string",
            "description": "Station code abbreviation (e.g. BVI)",
        },
        "arrival_time": {
            "type": "string",
            "description": "Scheduled arrival time HH:MM",
        },
        "departure_time": {
            "type": "string",
            "description": "Scheduled departure time HH:MM",
        },
        "platform": {
            "type": "string",
            "description": "Platform designation string (e.g. Platform 4) - Breaking change",
        },
        "status": {
            "type": "string",
            "description": "Current schedule status (e.g. ON_TIME)",
        },
    },
    "additionalProperties": False,
}

TRAIN_RUNNING_STATUS_V1_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrainRunningStatus",
    "type": "object",
    "required": [
        "train_number",
        "current_station",
        "next_station",
        "delay_minutes",
        "running_status",
        "last_updated",
    ],
    "properties": {
        "train_number": {
            "type": "string",
            "description": "Unique train identification number",
        },
        "current_station": {
            "type": "string",
            "description": "Current station code",
        },
        "next_station": {
            "type": "string",
            "description": "Upcoming station code",
        },
        "delay_minutes": {
            "type": "integer",
            "description": "Delay in minutes relative to schedule",
        },
        "running_status": {
            "type": "string",
            "description": "Operating status (e.g. ON_TIME, DELAYED, CANCELLED)",
        },
        "last_updated": {
            "type": "string",
            "description": "Timestamp of telemetry reading",
        },
    },
    "additionalProperties": False,
}


def seed_database(db: Session) -> dict[str, int]:
    """Populate demonstration data idempotently and return counts."""
    # 1. Producers
    producers_data = [
        {
            "name": "Railway Scheduling System",
            "description": "Source system managing train timetables, schedules, and platform assignments",
        },
        {
            "name": "Train Tracking System",
            "description": "Source system providing live train positioning, delays, and telemetry",
        },
    ]

    producer_map: dict[str, Producer] = {}
    for p_info in producers_data:
        prod = db.query(Producer).filter(Producer.name == p_info["name"]).first()
        if not prod:
            prod = Producer(name=p_info["name"], description=p_info["description"])
            db.add(prod)
            db.flush()
        producer_map[p_info["name"]] = prod

    # 2. Consumers
    consumers_data = [
        {
            "name": "Station Display System",
            "description": "Platform and concourse departure/arrival digital display boards",
        },
        {
            "name": "Passenger Information System",
            "description": "Public web portal, mobile app, and SMS notification service",
        },
        {
            "name": "Railway Analytics System",
            "description": "Internal business intelligence and operational reporting engine",
        },
    ]

    consumer_map: dict[str, Consumer] = {}
    for c_info in consumers_data:
        cons = db.query(Consumer).filter(Consumer.name == c_info["name"]).first()
        if not cons:
            cons = Consumer(name=c_info["name"], description=c_info["description"])
            db.add(cons)
            db.flush()
        consumer_map[c_info["name"]] = cons

    # 3. Contract 1: Train Schedule Contract
    schedule_contract_name = "Train Schedule Contract"
    schedule_contract = db.query(Contract).filter(Contract.name == schedule_contract_name).first()
    if not schedule_contract:
        schedule_contract = Contract(
            name=schedule_contract_name,
            description="Contract governing train timetable schedules and platform allocations",
            producer_id=producer_map["Railway Scheduling System"].id,
            consumers=[
                consumer_map["Station Display System"],
                consumer_map["Passenger Information System"],
                consumer_map["Railway Analytics System"],
            ],
        )
        db.add(schedule_contract)
        db.flush()
    else:
        schedule_contract.consumers = [
            consumer_map["Station Display System"],
            consumer_map["Passenger Information System"],
            consumer_map["Railway Analytics System"],
        ]

    # Train Schedule Versions (v1 and v2)
    v1 = (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == schedule_contract.id, ContractVersion.version_number == 1)
        .first()
    )
    if not v1:
        v1 = ContractVersion(
            contract_id=schedule_contract.id,
            version_number=1,
            schema_definition=TRAIN_SCHEDULE_V1_SCHEMA,
            description="Version 1: initial schedule schema with integer platform number",
        )
        db.add(v1)

    v2 = (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == schedule_contract.id, ContractVersion.version_number == 2)
        .first()
    )
    if not v2:
        v2 = ContractVersion(
            contract_id=schedule_contract.id,
            version_number=2,
            schema_definition=TRAIN_SCHEDULE_V2_SCHEMA,
            description="Version 2: platform changed from integer to string (breaking change demo)",
        )
        db.add(v2)

    # 4. Contract 2: Train Running Status Contract
    status_contract_name = "Train Running Status Contract"
    status_contract = db.query(Contract).filter(Contract.name == status_contract_name).first()
    if not status_contract:
        status_contract = Contract(
            name=status_contract_name,
            description="Contract governing real-time telemetry and running status updates",
            producer_id=producer_map["Train Tracking System"].id,
            consumers=[
                consumer_map["Passenger Information System"],
                consumer_map["Railway Analytics System"],
            ],
        )
        db.add(status_contract)
        db.flush()
    else:
        status_contract.consumers = [
            consumer_map["Passenger Information System"],
            consumer_map["Railway Analytics System"],
        ]

    # Train Running Status Version 1
    status_v1 = (
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == status_contract.id, ContractVersion.version_number == 1)
        .first()
    )
    if not status_v1:
        status_v1 = ContractVersion(
            contract_id=status_contract.id,
            version_number=1,
            schema_definition=TRAIN_RUNNING_STATUS_V1_SCHEMA,
            description="Version 1: initial running status telemetry schema",
        )
        db.add(status_v1)

    # 5. Semantic Rules for Train Running Status Contract
    # Rule 1: delay_minutes >= 0
    rule1 = (
        db.query(SemanticRule)
        .filter(
            SemanticRule.contract_id == status_contract.id,
            SemanticRule.rule_name == "delay_minutes_non_negative",
        )
        .first()
    )
    if not rule1:
        rule1 = SemanticRule(
            contract_id=status_contract.id,
            rule_name="delay_minutes_non_negative",
            field_name="delay_minutes",
            rule_type="MIN_VALUE",
            rule_expression="delay_minutes >= 0",
            parameters={"min": 0},
            error_message="delay_minutes cannot be negative",
        )
        db.add(rule1)

    # Rule 2: running_status in [ON_TIME, DELAYED, CANCELLED, ARRIVED]
    rule2 = (
        db.query(SemanticRule)
        .filter(
            SemanticRule.contract_id == status_contract.id,
            SemanticRule.rule_name == "valid_running_status",
        )
        .first()
    )
    if not rule2:
        rule2 = SemanticRule(
            contract_id=status_contract.id,
            rule_name="valid_running_status",
            field_name="running_status",
            rule_type="ALLOWED_VALUES",
            rule_expression="running_status in [ON_TIME, DELAYED, CANCELLED, ARRIVED]",
            parameters={"allowed_values": ["ON_TIME", "DELAYED", "CANCELLED", "ARRIVED"]},
            error_message="running_status has an invalid value",
        )
        db.add(rule2)

    db.commit()

    return {
        "producers": db.query(Producer).count(),
        "consumers": db.query(Consumer).count(),
        "contracts": db.query(Contract).count(),
        "contract_versions": db.query(ContractVersion).count(),
        "semantic_rules": db.query(SemanticRule).count(),
    }



def main():
    """CLI entry point to seed database."""
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    print("Seeding demonstration data...")
    with SessionLocal() as db:
        counts = seed_database(db)
        print(f"Seeding completed successfully: {counts}")


if __name__ == "__main__":
    main()
