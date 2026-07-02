"""
Fraud Detection Integration Examples

Shows how to migrate from legacy implementations to unified engine.
"""

from fraud_detection_unified import ConsolidatedFraudDetectionEngine


def migrate_mpesa_fraud_scoring():
    """
    Example: Migrate M-Pesa fraud scoring to unified engine.

    Before: Used mpesa_safaricom/fraud_anomaly_detection/fraud_engine/detector.py
    After: Uses ConsolidatedFraudDetectionEngine.score_mobile_money_transaction()
    """
    engine = ConsolidatedFraudDetectionEngine(
        config={
            "model_path": "fraud_detection_unified/models/fraud_model_v1.joblib",
            "ml_fraud_threshold": 0.7,
            "velocity_threshold_60s": 10,
        }
    )

    # Example M-Pesa transaction
    mpesa_txn = {
        "txn_id": "TXN_20250108_001",
        "amount": 75000,
        "velocity_60s": 12,  # High velocity
        "sim_swap_days": 1,
        "timestamp": "2025-01-08T23:45:00",
        "institution": "MPESA"
    }

    alert = engine.score_mobile_money_transaction(mpesa_txn)
    print(f"M-Pesa Alert: {alert.alert_message}")
    engine.log_alert(alert)

    return engine


def migrate_aml_detection():
    """
    Example: Migrate banking AML detection to unified engine.

    Before: Used kenya_banking_sector/aml_transaction_monitoring/src/rules_engine.py
    After: Uses ConsolidatedFraudDetectionEngine.score_banking_transaction()
    """
    engine = ConsolidatedFraudDetectionEngine(
        config={
            "high_value_threshold": 500000,
            "structuring_threshold": 900000,
            "structuring_limit": 1000000,
            "structuring_min_count": 3,
        }
    )

    # Example banking transaction (PEP + high value)
    banking_txn = {
        "txn_id": "BNK_20250108_5401",
        "account_id": "ACC_9999",
        "amount": 850000,  # Near structuring threshold
        "txn_type": "Cash Deposit",
        "is_pep": True,
        "recent_txn_count_48h": 4,
        "timestamp": "2025-01-08T10:30:00",
        "institution": "KCB_BANK"
    }

    alert = engine.score_banking_transaction(banking_txn)
    print(f"AML Alert: {alert.alert_message}")
    engine.log_alert(alert)

    return engine


def unified_fraud_detection_flow():
    """
    Example: Process multiple transactions through unified engine.
    """
    engine = ConsolidatedFraudDetectionEngine()

    # Mix of M-Pesa and banking transactions
    transactions = [
        {
            "type": "mobile_money",
            "data": {
                "txn_id": "MP_1",
                "amount": 50000,
                "velocity_60s": 15,
                "sim_swap_days": -1,
                "timestamp": "2025-01-08T10:00:00",
                "institution": "MPESA"
            }
        },
        {
            "type": "banking",
            "data": {
                "txn_id": "BK_1",
                "account_id": "ACC_001",
                "amount": 450000,
                "txn_type": "Transfer",
                "is_pep": False,
                "recent_txn_count_48h": 2,
                "timestamp": "2025-01-08T11:00:00",
                "institution": "EQUITY_BANK"
            }
        }
    ]

    for txn_item in transactions:
        if txn_item["type"] == "mobile_money":
            alert = engine.score_mobile_money_transaction(txn_item["data"])
        else:
            alert = engine.score_banking_transaction(txn_item["data"])

        engine.log_alert(alert)
        if alert.severity in ["HIGH", "CRITICAL"]:
            print(f"⚠️  ALERT: {alert.alert_message}")

    # Print summary
    summary = engine.get_alerts_summary()
    print(f"\n📊 Summary: {summary['total_alerts']} alerts processed")
    print(f"   By severity: {summary['by_severity']}")


if __name__ == "__main__":
    print("=== M-Pesa Fraud Scoring ===")
    migrate_mpesa_fraud_scoring()

    print("\n=== AML Detection ===")
    migrate_aml_detection()

    print("\n=== Unified Multi-Type Processing ===")
    unified_fraud_detection_flow()
