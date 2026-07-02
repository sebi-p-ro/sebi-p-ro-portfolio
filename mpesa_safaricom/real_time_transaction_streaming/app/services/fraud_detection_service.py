"""
Streaming Fraud Detection Service

Integrates ConsolidatedFraudDetectionEngine into the real-time transaction
pipeline. Consumes raw transactions from Kafka, applies fraud scoring, and
publishes alerts to the warehouse for dashboard consumption.
"""

import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from queue import Queue

from fraud_detection_unified import ConsolidatedFraudDetectionEngine

logger = logging.getLogger(__name__)


class StreamingFraudDetectionService:
    """
    Real-time fraud detection for transaction stream.

    Intended deployment:
    1. Run as a separate consumer group in Kafka deployment
    2. Consume transactions from raw_transactions topic
    3. Score each transaction with fraud engine
    4. Produce fraud_alerts to dedicated topic for warehouse ingestion
    5. Optional: Publish high-severity alerts to SQS/SNS for immediate action
    """

    def __init__(
        self,
        fraud_engine_config: Optional[Dict[str, Any]] = None,
        batch_size: int = 100,
        alert_queue_size: int = 10000,
    ):
        """
        Initialize streaming fraud detection service.

        Args:
            fraud_engine_config: Configuration for ConsolidatedFraudDetectionEngine
            batch_size: Number of transactions to batch before warehouse write
            alert_queue_size: Max alerts to hold in memory before flushing
        """
        self.engine = ConsolidatedFraudDetectionEngine(fraud_engine_config or {})
        self.batch_size = batch_size
        self.alert_queue_size = alert_queue_size
        self.alert_buffer: Queue = Queue(maxsize=alert_queue_size)
        self.stats = {
            "transactions_processed": 0,
            "alerts_generated": 0,
            "errors": 0,
            "high_severity": 0,
        }
        self._lock = threading.RLock()

    def process_transaction(self, txn_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single transaction through fraud detection.

        Args:
            txn_data: Raw transaction data from Kafka

        Returns:
            Alert dict if fraud detected, None otherwise
        """
        try:
            # Determine transaction type
            txn_type = txn_data.get("txn_type", "unknown").lower()
            institution = txn_data.get("institution", "MPESA")

            # Route to appropriate scorer
            if "mpesa" in institution.lower() or txn_type in ["c2b", "b2c", "b2b"]:
                alert = self.engine.score_mobile_money_transaction(txn_data)
            else:
                alert = self.engine.score_banking_transaction(txn_data)

            # Record stats
            with self._lock:
                self.stats["transactions_processed"] += 1
                if alert.severity in ["HIGH", "CRITICAL"]:
                    self.stats["high_severity"] += 1
                if alert.risk_score > 0.5:
                    self.stats["alerts_generated"] += 1

            # Convert alert to exportable format
            if alert.risk_score > 0.5 or alert.severity in ["HIGH", "CRITICAL"]:
                alert_dict = {
                    "alert_id": self._generate_alert_id(),
                    "transaction_id": alert.transaction_id,
                    "institution": alert.institution,
                    "detected_type": alert.detected_type,
                    "risk_score": alert.risk_score,
                    "severity": alert.severity,
                    "rules_triggered": "|".join(alert.rules_triggered),  # For CSV export
                    "timestamp": alert.timestamp,
                "alert_message": alert.alert_message,
                "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            }
                return alert_dict
            return None

        except Exception as e:
            logger.error(f"Error processing transaction {txn_data.get('txn_id')}: {e}")
            with self._lock:
                self.stats["errors"] += 1
            return None

    def process_batch(self, transactions: list) -> list:
        """
        Process a batch of transactions.

        Args:
            transactions: List of raw transaction dicts

        Returns:
            List of fraud alerts generated
        """
        alerts = []
        for txn in transactions:
            alert = self.process_transaction(txn)
            if alert:
                alerts.append(alert)
        return alerts

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        import uuid
        return f"ALERT_{uuid.uuid4().hex[:12].upper()}"

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        with self._lock:
            return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            for key in self.stats:
                self.stats[key] = 0

    def format_for_warehouse(self, alerts: list) -> list:
        """
        Format alerts for database ingestion.

        Expected schema:
        ```
        CREATE TABLE fraud_alerts (
            alert_id VARCHAR(255) PRIMARY KEY,
            transaction_id VARCHAR(255),
            institution VARCHAR(100),
            detected_type VARCHAR(50),
            risk_score FLOAT,
            severity VARCHAR(20),
            rules_triggered TEXT,
            detected_timestamp TIMESTAMP,
            ingestion_timestamp TIMESTAMP
        )
        ```
        """
        formatted = []
        for alert in alerts:
            formatted.append({
                "alert_id": alert["alert_id"],
                "transaction_id": alert["transaction_id"],
                "institution": alert["institution"],
                "detected_type": alert["detected_type"],
                "risk_score": float(alert["risk_score"]),
                "severity": alert["severity"],
                "rules_triggered": alert["rules_triggered"],
                "detected_timestamp": alert["timestamp"],
                "ingestion_timestamp": alert["ingestion_timestamp"],
            })
        return formatted

    def serialize_for_kafka(self, alert: Dict[str, Any]) -> str:
        """Serialize alert for Kafka publication."""
        # Remove fields that aren't JSON-serializable
        serializable = {
            k: v for k, v in alert.items()
            if isinstance(v, (str, int, float, bool, type(None)))
        }
        return json.dumps(serializable, default=str)


# Example Kafka Consumer Integration
# This shows how to use StreamingFraudDetectionService with a Kafka consumer

class KafkaStreamingConsumer:
    """
    Kafka consumer for fraud detection.

    Usage:
    ```
    consumer = KafkaStreamingConsumer(
        bootstrap_servers=["localhost:9092"],
        input_topic="transactions_raw",
        alert_topic="fraud_alerts",
        group_id="fraud_detection_group"
    )
    consumer.run()
    ```
    """

    KafkaConsumer = None
    KafkaProducer = None

    def __init__(
        self,
        bootstrap_servers: list,
        input_topic: str,
        alert_topic: str,
        group_id: str,
        consumer_config: Optional[Dict] = None,
    ):
        """Initialize Kafka consumer for fraud detection."""
        self.bootstrap_servers = bootstrap_servers
        self.input_topic = input_topic
        self.alert_topic = alert_topic
        self.group_id = group_id
        self.consumer_config = consumer_config or {}
        self.fraud_service = StreamingFraudDetectionService()
        
        # Lazy import to avoid hard dependency on kafka-python
        try:
            from kafka import KafkaConsumer, KafkaProducer
            self.KafkaConsumer = KafkaConsumer
            self.KafkaProducer = KafkaProducer
        except ImportError:
            logger.warning(
                "kafka-python not installed. Consumer mock mode only. "
                "Install with: pip install kafka-python"
            )
            self.KafkaConsumer = None
            self.KafkaProducer = None

    def run(self, timeout_ms: int = 1000) -> None:
        """
        Start consuming transactions and detecting fraud.

        Args:
            timeout_ms: Consumer poll timeout in milliseconds
        """
        if not self.KafkaConsumer:
            logger.error("kafka-python not available. Cannot run consumer.")
            return

        consumer = self.KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            **self.consumer_config,
        )

        producer = self.KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

        logger.info(f"Fraud detection consumer started on topic {self.input_topic}")

        batch = []
        try:
            for message in consumer:
                txn = message.value
                batch.append(txn)

                # Process batch when threshold reached
                if len(batch) >= self.fraud_service.batch_size:
                    alerts = self.fraud_service.process_batch(batch)
                    for alert in alerts:
                        producer.send(self.alert_topic, value=alert)
                        logger.debug(
                            f"Published alert for {alert['transaction_id']}: "
                            f"{alert['severity']}"
                        )
                    batch = []

        except KeyboardInterrupt:
            logger.info("Fraud detection consumer shutting down...")
        finally:
            consumer.close()
            producer.close()
            stats = self.fraud_service.get_stats()
            logger.info(f"Final stats: {stats}")


if __name__ == "__main__":
    # Example: Mock processing for testing
    service = StreamingFraudDetectionService()

    sample_txns = [
        {
            "txn_id": "TXN_001",
            "amount": 75000,
            "velocity_60s": 12,
            "sim_swap_days": 1,
            "timestamp": "2025-01-08T23:45:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        },
        {
            "txn_id": "TXN_002",
            "amount": 15000,
            "velocity_60s": 2,
            "sim_swap_days": -1,
            "timestamp": "2025-01-09T08:30:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        },
    ]

    print("Processing sample transactions...")
    alerts = service.process_batch(sample_txns)
    print(f"Generated {len(alerts)} alerts")
    for alert in alerts:
        print(f"  - {alert['alert_id']}: {alert['severity']} {alert['rules_triggered']}")

    print(f"Stats: {service.get_stats()}")
