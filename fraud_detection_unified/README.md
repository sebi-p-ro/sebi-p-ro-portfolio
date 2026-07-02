# Consolidated Fraud Detection Engine

**Status**: 🟡 Working example consolidating multiple fraud detection systems into one canonical implementation.

## Overview

This module consolidates fraud detection logic from multiple projects into a single, configurable engine:

- **M-Pesa Real-Time Fraud Detection** (from `mpesa_safaricom/fraud_anomaly_detection`)
  - ML-based fraud scoring for mobile money transactions
  - Rules for velocity spikes, SIM swaps, night transactions

- **Banking Sector AML Monitoring** (from `kenya_banking_sector/aml_transaction_monitoring`)
  - Rules-based detection for structuring, PEP transactions, velocity
  - Account-level aggregation for suspicious patterns

## Architecture

```
ConsolidatedFraudDetectionEngine
├── score_mobile_money_transaction()   # M-Pesa specific
├── score_banking_transaction()        # Banking sector specific
├── log_alert()                        # Audit trail
└── get_alerts_summary()               # Reporting
```

Both scoring methods return standardized `FraudAlert` objects with:
- Risk score (0.0 - 1.0)
- Severity level (LOW, MEDIUM, HIGH, CRITICAL)
- Rules triggered
- Structured alert message

## Configuration

```python
config = {
    "model_path": "fraud_detection_unified/models/fraud_model_v1.joblib",
    "ml_fraud_threshold": 0.7,
    "velocity_threshold_60s": 10,
    "high_value_threshold": 500000,
    "structuring_threshold": 900000,
}
engine = ConsolidatedFraudDetectionEngine(config)
```

## Migration Path

### From M-Pesa Detector

**Old**:
```python
from mpesa_safaricom.fraud_anomaly_detection.fraud_engine.detector import MpesaFraudDetector
detector = MpesaFraudDetector()
result = detector.score_transaction(txn_data)
```

**New**:
```python
from fraud_detection_unified import ConsolidatedFraudDetectionEngine
engine = ConsolidatedFraudDetectionEngine()
alert = engine.score_mobile_money_transaction(txn_data)
```

### From AML Rules Engine

**Old**:
```python
from kenya_banking_sector.aml_transaction_monitoring.src.rules_engine import AMLRulesEngine
aml = AMLRulesEngine()
alerts = aml.run_structuring_rule()
```

**New**:
```python
from fraud_detection_unified import ConsolidatedFraudDetectionEngine
engine = ConsolidatedFraudDetectionEngine()
alert = engine.score_banking_transaction(txn_data)
```

## Usage

```python
from fraud_detection_unified import ConsolidatedFraudDetectionEngine

# Initialize
engine = ConsolidatedFraudDetectionEngine()

# Score M-Pesa transaction
mpesa_alert = engine.score_mobile_money_transaction({
    "txn_id": "TXN_001",
    "amount": 75000,
    "velocity_60s": 12,
    "sim_swap_days": 1,
    "timestamp": "2025-01-08T23:45:00",
    "institution": "MPESA"
})

# Score banking transaction
banking_alert = engine.score_banking_transaction({
    "txn_id": "BNK_001",
    "account_id": "ACC_9999",
    "amount": 850000,
    "txn_type": "Cash Deposit",
    "is_pep": True,
    "timestamp": "2025-01-08T10:30:00",
    "institution": "KCB_BANK"
})

# Log and report
engine.log_alert(mpesa_alert)
engine.log_alert(banking_alert)
summary = engine.get_alerts_summary()
engine.export_alerts("fraud_alerts_export.csv")
```

## Integration Points

This engine is intended to replace:

1. `mpesa_safaricom/fraud_anomaly_detection/fraud_engine/detector.py`
2. `kenya_banking_sector/aml_transaction_monitoring/src/rules_engine.py`
3. References in `master_dashboard.py`
4. `mpesa_safaricom/merchant_intelligence_platform` (for fraud risk scoring)

## Configurability

The engine supports adding new rules via configuration:

```python
engine = ConsolidatedFraudDetectionEngine(
    config={
        "velocity_threshold_60s": 20,        # Custom threshold
        "structuring_min_count": 5,          # Custom structuring pattern
        "ml_fraud_threshold": 0.65,          # Custom ML threshold
    }
)
```

## Files

- `engine.py` — Core fraud detection logic
- `examples.py` — Migration examples
- `models/` — Placeholder for fraud model artifacts
- `README.md` — This file

## Known Limitations

- **ML Model**: Assumes pre-trained joblib model exists. Falls back to rules-only if missing.
- **Feature Engineering**: M-Pesa rules use timestamp-based features; banking rules are account-centric.
- **Audit Trail**: In-memory alerts log. For production, integrate with centralized logging (ELK, DataDog, etc.).
- **Real-time Requirements**: Current implementation is transaction-batch suitable; for true streaming, integrate with Kafka/Kinesis.

## Next Steps

1. Deploy consolidated engine as API service
2. Integrate with transaction processing pipelines (dbt + Airflow)
3. Add monitoring/alerting for rule threshold tuning
4. Consolidate dashboards to use unified engine
5. Deprecate legacy fraud modules after successful migration
