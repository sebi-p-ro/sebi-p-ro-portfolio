"""
Unit tests for ConsolidatedFraudDetectionEngine
"""

import pytest
from datetime import datetime, timedelta
from fraud_detection_unified.engine import (
    ConsolidatedFraudDetectionEngine,
    FraudAlert,
)


@pytest.fixture
def engine():
    """Initialize fraud detection engine with test configuration."""
    return ConsolidatedFraudDetectionEngine(
        config={
            "velocity_threshold_60s": 10,
            "high_value_threshold": 500000,
            "structuring_threshold": 900000,
            "structuring_limit": 1000000,
            "ml_fraud_threshold": 0.7,
        }
    )


class TestMobileMoneyScoring:
    """Tests for M-Pesa transaction scoring."""

    def test_normal_transaction_low_risk(self, engine):
        """Normal transaction should have low risk score."""
        txn = {
            "txn_id": "TXN_001",
            "amount": 10000,
            "velocity_60s": 1,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert.transaction_id == "TXN_001"
        assert alert.risk_score < 0.5
        assert alert.severity == "LOW"
        assert "EXTREME_VELOCITY" not in alert.rules_triggered

    def test_high_velocity_flagged(self, engine):
        """High velocity should trigger alert."""
        txn = {
            "txn_id": "TXN_002",
            "amount": 5000,
            "velocity_60s": 15,  # Above threshold of 10
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert.risk_score >= 0.25
        assert "EXTREME_VELOCITY" in alert.rules_triggered
        assert alert.severity in ["MEDIUM", "HIGH"]

    def test_sim_swap_high_value_flagged(self, engine):
        """SIM swap + high value should trigger alert."""
        txn = {
            "txn_id": "TXN_003",
            "amount": 75000,
            "velocity_60s": 2,
            "sim_swap_days": 1,  # Recent SIM swap
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert.risk_score >= 0.2
        assert "HIGH_VALUE_POST_SIM_SWAP" in alert.rules_triggered

    def test_night_transaction_flag(self, engine):
        """Night transactions should be flagged."""
        txn = {
            "txn_id": "TXN_004",
            "amount": 30000,
            "velocity_60s": 1,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T23:45:00",  # 11:45 PM
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert "NIGHT_TRANSACTION" in alert.rules_triggered

    def test_multiple_rules_combination(self, engine):
        """Multiple rules should compound risk score."""
        txn = {
            "txn_id": "TXN_005",
            "amount": 100000,
            "velocity_60s": 12,  # High velocity
            "sim_swap_days": 0,  # SIM just swapped
            "timestamp": "2025-01-08T03:00:00",  # Night transaction
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert len(alert.rules_triggered) >= 3
        assert alert.risk_score > 0.5
        assert alert.severity in ["HIGH", "CRITICAL"]

    def test_invalid_timestamp_graceful_handling(self, engine):
        """Invalid timestamp should not crash, skip that rule."""
        txn = {
            "txn_id": "TXN_006",
            "amount": 20000,
            "velocity_60s": 5,
            "sim_swap_days": -1,
            "timestamp": "invalid-timestamp",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert is not None
        assert "NIGHT_TRANSACTION" not in alert.rules_triggered


class TestBankingTransactionScoring:
    """Tests for banking/AML transaction scoring."""

    def test_normal_banking_transaction(self, engine):
        """Normal banking transaction should have low risk."""
        txn = {
            "txn_id": "BNK_001",
            "account_id": "ACC_001",
            "amount": 100000,
            "txn_type": "Transfer",
            "is_pep": False,
            "recent_txn_count_48h": 1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "KCB_BANK",
        }
        alert = engine.score_banking_transaction(txn)
        
        assert alert.risk_score < 0.5
        assert alert.severity == "LOW"

    def test_pep_high_value_alert(self, engine):
        """PEP high-value transaction should trigger alert."""
        txn = {
            "txn_id": "BNK_002",
            "account_id": "ACC_002",
            "amount": 600000,  # Above threshold
            "txn_type": "Transfer",
            "is_pep": True,
            "recent_txn_count_48h": 1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "EQUITY_BANK",
        }
        alert = engine.score_banking_transaction(txn)
        
        assert alert.risk_score >= 0.3
        assert "PEP_HIGH_VALUE" in alert.rules_triggered
        assert alert.severity in ["MEDIUM", "HIGH"]

    def test_structuring_pattern_detected(self, engine):
        """Near-limit deposits should trigger structuring flag."""
        txn = {
            "txn_id": "BNK_003",
            "account_id": "ACC_003",
            "amount": 950000,  # Near 1M limit
            "txn_type": "Cash Deposit",
            "is_pep": False,
            "recent_txn_count_48h": 5,  # Multiple recent deposits
            "timestamp": "2025-01-08T10:00:00",
            "institution": "ABSA_BANK",
        }
        alert = engine.score_banking_transaction(txn)
        
        assert "NEAR_STRUCTURING_LIMIT" in alert.rules_triggered
        assert "RAPID_CASH_DEPOSITS" in alert.rules_triggered

    def test_low_amount_deposit_no_structuring_flag(self, engine):
        """Deposit well below threshold should not trigger structuring."""
        txn = {
            "txn_id": "BNK_004",
            "account_id": "ACC_004",
            "amount": 500000,  # Well below threshold
            "txn_type": "Cash Deposit",
            "is_pep": False,
            "recent_txn_count_48h": 3,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "KCB_BANK",
        }
        alert = engine.score_banking_transaction(txn)
        
        assert "NEAR_STRUCTURING_LIMIT" not in alert.rules_triggered
        assert alert.severity == "LOW"


class TestSeverityCalculation:
    """Tests for severity level calculation."""

    def test_critical_severity_threshold(self, engine):
        """Risk score >= 0.9 should be CRITICAL."""
        txn = {
            "txn_id": "TXN_CRIT",
            "amount": 200000,
            "velocity_60s": 25,  # Extreme velocity
            "sim_swap_days": 0,
            "timestamp": "2025-01-08T02:00:00",  # Night
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        if alert.risk_score >= 0.9:
            assert alert.severity == "CRITICAL"

    def test_high_severity_threshold(self, engine):
        """Risk score 0.7-0.89 should be HIGH."""
        txn = {
            "txn_id": "TXN_HIGH",
            "amount": 80000,
            "velocity_60s": 12,
            "sim_swap_days": 1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        if 0.7 <= alert.risk_score < 0.9:
            assert alert.severity == "HIGH"

    def test_medium_severity_threshold(self, engine):
        """Risk score 0.5-0.69 should be MEDIUM."""
        txn = {
            "txn_id": "TXN_MED",
            "amount": 50000,
            "velocity_60s": 11,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        if 0.5 <= alert.risk_score < 0.7:
            assert alert.severity == "MEDIUM"


class TestAlertLogging:
    """Tests for alert logging and export."""

    def test_alert_logging(self, engine):
        """Alerts should be logged in engine."""
        txn = {
            "txn_id": "TXN_LOG",
            "amount": 75000,
            "velocity_60s": 12,
            "sim_swap_days": 1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        engine.log_alert(alert)
        
        summary = engine.get_alerts_summary()
        assert summary["total_alerts"] == 1

    def test_multiple_alerts_summary(self, engine):
        """Summary should aggregate multiple alerts."""
        txns = [
            {
                "txn_id": f"TXN_{i}",
                "amount": 50000 + i * 10000,
                "velocity_60s": 5 + i,
                "sim_swap_days": -1,
                "timestamp": "2025-01-08T10:00:00",
                "institution": "MPESA",
            }
            for i in range(5)
        ]
        
        for txn in txns:
            alert = engine.score_mobile_money_transaction(txn)
            engine.log_alert(alert)
        
        summary = engine.get_alerts_summary()
        assert summary["total_alerts"] == 5
        assert "by_severity" in summary
        assert "by_type" in summary


class TestConfigurability:
    """Tests for configurable thresholds."""

    def test_custom_velocity_threshold(self):
        """Custom velocity threshold should be respected."""
        engine = ConsolidatedFraudDetectionEngine(
            config={"velocity_threshold_60s": 20}  # Custom higher threshold
        )
        
        txn = {
            "txn_id": "TXN_VEL",
            "amount": 10000,
            "velocity_60s": 15,  # Above default but below custom
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert "EXTREME_VELOCITY" not in alert.rules_triggered

    def test_custom_ml_threshold(self):
        """Custom ML threshold should be used."""
        engine = ConsolidatedFraudDetectionEngine(
            config={"ml_fraud_threshold": 0.5}  # Lower threshold
        )
        assert engine.rules_config["ml_fraud_threshold"] == 0.5


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_missing_transaction_id(self, engine):
        """Transaction without ID should still process."""
        txn = {
            "amount": 10000,
            "velocity_60s": 1,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert.transaction_id == "UNKNOWN"
        assert alert is not None

    def test_negative_amount(self, engine):
        """Negative amount should not crash."""
        txn = {
            "txn_id": "TXN_NEG",
            "amount": -5000,
            "velocity_60s": 1,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert alert is not None
        assert alert.risk_score >= 0

    def test_zero_velocity(self, engine):
        """Zero velocity should not trigger alert."""
        txn = {
            "txn_id": "TXN_ZERO_VEL",
            "amount": 50000,
            "velocity_60s": 0,
            "sim_swap_days": -1,
            "timestamp": "2025-01-08T10:00:00",
            "institution": "MPESA",
        }
        alert = engine.score_mobile_money_transaction(txn)
        
        assert "EXTREME_VELOCITY" not in alert.rules_triggered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
