"""Standalone Kafka Consumer Runner for Contract Guard.

Runs a continuous background loop consuming streaming contract events,
routing each to the Phase 8 RuntimeValidationService, and committing offsets.

Usage:
    python -m app.kafka_consumer_runner
"""

import logging
import signal
import sys
import time

from app.config import get_settings
from app.database import SessionLocal
from app.services.kafka_consumer import KafkaConsumerService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("kafka_consumer_runner")


def run_consumer_loop() -> None:
    """Run the blocking Kafka consumption loop until interrupted."""
    settings = get_settings()
    logger.info("Initializing Contract Guard Kafka Consumer...")
    logger.info("  Bootstrap Servers : %s", settings.kafka_bootstrap_servers)
    logger.info("  Topic             : %s", settings.kafka_topic)
    logger.info("  Consumer Group    : %s", settings.kafka_consumer_group)

    consumer_service = KafkaConsumerService()
    running = True

    def handle_shutdown(signum, frame):
        nonlocal running
        logger.info("Shutdown signal received (%s). Stopping consumer loop...", signum)
        running = False

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info("Kafka consumer is now listening for events. Press Ctrl+C to terminate.")

    try:
        while running:
            # Open an isolated DB session for each poll iteration
            db = SessionLocal()
            try:
                result = consumer_service.consume_message(db=db, timeout=1.0)
                if result is not None:
                    event_id = result.get("event_id", "unknown")
                    status = result.get("status")
                    if status == "SUCCESS":
                        is_valid = result.get("valid")
                        logger.info(
                            "-> Processed event '%s': Validation result = %s",
                            event_id,
                            "VALID" if is_valid else "INVALID",
                        )
                    else:
                        logger.error(
                            "-> Failed processing event '%s' [%s]: %s",
                            event_id,
                            result.get("error_type"),
                            result.get("message"),
                        )
            except Exception as exc:
                logger.error("Unexpected error in consumer loop: %s", exc, exc_info=True)
                time.sleep(1.0)
            finally:
                db.close()
    finally:
        logger.info("Closing Kafka consumer connection...")
        consumer_service.close()
        logger.info("Kafka consumer shutdown complete.")


if __name__ == "__main__":
    run_consumer_loop()
