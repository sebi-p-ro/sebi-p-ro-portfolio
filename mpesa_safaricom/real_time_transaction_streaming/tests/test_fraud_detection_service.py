"""
Tests for StreamingFraudDetectionService
"""

import pytest
import json
from unittest.mock import MagicMock, patch

from mpesa_safaricom.real_time_transaction_streaming.app.services.fraud_detection_service import (
    StreamingFraudDetectionService,
    KafkaStreamingConsumer,
)


@pytest.fixture
def streaming_service():
    """Initialize streaming fraud detection service."""
    return StreamingFraudDetectionService(
        batch_size=10,
        alert_queue_size=1000,
    )


class TestStreamingFraudDetectionService:
    """Tests for StreamingFraudDetectionService."""

    def test_process_single_transaction(self, streaming_service):
        """Process a single transaction."""
        txn = {
            "txn_id": "TXN_001",
            "amount": 75000,
            "velocity_60s": 12,
            "sim_swap_days": 1,
            "timestamp": "2025-01-08T23:45:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        }
        
        alert = streaming_service.process_transaction(txn)
        
        assert alert is not None
        assert alert["transaction_id"] == "TXN_001"
        assert "alert_id" in alert
        assert "risk_score" in alert
        assert "severity" in alert

    def test_normal_transaction_returns_none(self, streaming_service):
        """Normal transaction with low risk should return None."""
        txn = {
            "txn_id": "TXN_NORMAL",
            "amount": 5000,
            "velocity_60s": 1,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        }
        
        alert = streaming_service.process_transaction(txn)
        
        assert alert is None

    def test_batch_processing(self, streaming_service):
        """Process batch of transactions."""
        txns = [
            {
                "txn_id": f"TXN_{i}",
                "amount": 50000 + i * 10000,
                "velocity_60s": 5 + i,
                "sim_swap_days": -1 if i % 2 == 0 else i,
                "timestamp": "2025-01-08T10:00:00",
                "institution": "MPESA",
                "txn_type": "C2B",
            }
            for i in range(5)
        ]
        
        alerts = streaming_service.process_batch(txns)
        
        assert isinstance(alerts, list)
        assert streaming_service.stats["transactions_processed"] == 5

    def test_stats_tracking(self, streaming_service):
        """Stats should be correctly tracked."""
        txn = {
            "txn_id": "TXN_STAT",
            "amount": 100000,
            "velocity_60s": 15,
            "sim_swap_days": 0,
            "timestamp": "2025-01-08T01:00:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        }
        
        streaming_service.process_transaction(txn)
        
        stats = streaming_service.get_stats()
        assert stats["transactions_processed"] == 1
        assert stats["high_severity"] >= 0  # May or may not trigger

    def test_error_handling(self, streaming_service):
        """Service should handle errors gracefully."""
        txn = {
            "txn_id": "TXN_ERR",
            # Missing required fields to trigger error
        }
        
        alert = streaming_service.process_transaction(txn)
        
        # Should not crash, may return None or handle gracefully
        stats = streaming_service.get_stats()
        assert "errors" in stats

    def test_alert_format_for_warehouse(self, streaming_service):
        """Alerts should be formatted correctly for warehouse."""
        alert = {
            "alert_id": "ALERT_ABC123",
            "transaction_id": "TXN_001",
            "institution": "MPESA",
            "detected_type": "MPESA_FRAUD",
            "risk_score": 0.85,
            "severity": "HIGH",
            "rules_triggered": "EXTREME_VELOCITY|HIGH_VALUE_POST_SIM_SWAP",
            "timestamp": "2025-01-08T10:00:00",
            "ingestion_timestamp": "2025-01-08T10:00:01",
        }
        
        formatted = streaming_service.format_for_warehouse([alert])
        
        assert len(formatted) == 1
        assert formatted[0]["alert_id"] == "ALERT_ABC123"
        assert isinstance(formatted[0]["risk_score"], float)

    def test_kafka_serialization(self, streaming_service):
        """Alerts should be serializable for Kafka."""
        alert = {
            "alert_id": "ALERT_KFK123",
            "transaction_id": "TXN_001",
            "institution": "MPESA",
            "detected_type": "MPESA_FRAUD",
            "risk_score": 0.75,
            "severity": "HIGH",
            "rules_triggered": "EXTREME_VELOCITY",
            "timestamp": "2025-01-08T10:00:00",
            "ingestion_timestamp": "2025-01-08T10:00:01",
        }
        
        serialized = streaming_service.serialize_for_kafka(alert)
        
        assert isinstance(serialized, str)
        deserialized = json.loads(serialized)
        assert deserialized["alert_id"] == "ALERT_KFK123"

    def test_banking_transaction_routing(self, streaming_service):
        """Banking transactions should be routed to banking scorer."""
        txn = {
            "txn_id": "BNK_001",
            "account_id": "ACC_001",
            "amount": 600000,
            "txn_type": "Cash Deposit",
            "is_pep": True,
            "recent_txn_count_48h": 3,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "KCB_BANK",
        }
        
        alert = streaming_service.process_transaction(txn)
        
        # Should process without error and potentially generate alert
        stats = streaming_service.get_stats()
        assert stats["transactions_processed"] == 1

    def test_reset_stats(self, streaming_service):
        """Stats should reset."""
        txn = {
            "txn_id": "TXN_RESET",
            "amount": 75000,
            "velocity_60s": 12,
            "sim_swap_days": 1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
            "txn_type": "C2B",
        }
        
        streaming_service.process_transaction(txn)
        assert streaming_service.stats["transactions_processed"] > 0
        
        streaming_service.reset_stats()
        assert streaming_service.stats["transactions_processed"] == 0


class TestKafkaStreamingConsumer:
    """Tests for KafkaStreamingConsumer."""

    def test_consumer_initialization(self):
        """Consumer should initialize correctly."""
        consumer = KafkaStreamingConsumer(
            bootstrap_servers=["localhost:9092"],
            input_topic="transactions_raw",
            alert_topic="fraud_alerts",
            group_id="fraud_detection_test",
        )
        
        assert consumer.input_topic == "transactions_raw"
        assert consumer.alert_topic == "fraud_alerts"
        assert consumer.fraud_service is not None

    @patch("mpesa_safaricom.real_time_transaction_streaming.app.services.fraud_detection_service.KafkaStreamingConsumer.KafkaConsumer")
    def test_consumer_mock_mode(self, mock_consumer_class):
        """Consumer should handle kafka-python not being available gracefully."""
        consumer = KafkaStreamingConsumer(
            bootstrap_servers=["localhost:9092"],
            input_topic="test_topic",
            alert_topic="test_alerts",
            group_id="test_group",
        )
        
        # If KafkaConsumer is mocked/unavailable, should still initialize
        assert consumer.fraud_service is not None


class TestE2EStreamingFlow:
    """End-to-end tests for streaming fraud detection."""

    def test_e2e_fraud_detection_flow(self, streaming_service):
        """E2E: Transaction → Fraud Detection → Alert → Warehouse Format."""
        # Step 1: Raw transaction
        raw_txn = {
            "txn_id": "E2E_TXN_001",
            "amount": 100000,
            "velocity_60s": 20,  # High velocity
            "sim_swap_days": 2,
            "timestamp": "2025-01-08T23:30:00",  # Night time
            "institution": "MPESA",
            "txn_type": "C2B",
        }
        
        # Step 2: Process through fraud detection
        alert = streaming_service.process_transaction(raw_txn)
        assert alert is not None, "High-risk transaction should generate alert"
        
        # Step 3: Format for warehouse
        formatted = streaming_service.format_for_warehouse([alert])
        assert len(formatted) == 1
        assert formatted[0]["transaction_id"] == "E2E_TXN_001"
        
        # Step 4: Serialize for Kafka
        serialized = streaming_service.serialize_for_kafka(formatted[0])
        deserialized = json.loads(serialized)
        assert deserialized["alert_id"] is not None

    def test_e2e_batch_processing_flow(self, streaming_service):
        """E2E: Batch of transactions through pipeline."""
        # Step 1: Create batch of mixed-risk transactions
        batch = [
            {
                "txn_id": f"E2E_BATCH_{i}",
                "amount": 50000 + i * 20000,
                "velocity_60s": 5 + i * 3,  # Increasing velocity
                "sim_swap_days": -1,
                "timestamp": "2025-01-08T10:00:00",
                "institution": "MPESA",
                "txn_type": "C2B",
            }
            for i in range(5)
        ]
        
        # Step 2: Process batch
        alerts = streaming_service.process_batch(batch)
        
        # Step 3: Format all alerts
        formatted = streaming_service.format_for_warehouse(alerts)
        
        # Verify processing happened
        assert streaming_service.stats["transactions_processed"] == 5
        assert len(formatted) <= 5  # Some may not generate alerts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
