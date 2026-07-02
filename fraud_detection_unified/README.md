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

| Limitation | Impact | Production Workaround |
|-----------|--------|---------------------|
| **ML Model Missing** | Falls back to rules only | Train and deploy ML model; add model versioning |
| **Audit Trail In-Memory** | No persistent fraud history | Integrate with PostgreSQL or data warehouse |
| **Rules Hardcoded** | Cannot tune without code changes | Externalize rules to database/config service |
| **Single-Threaded** | Slow batch processing | Implement distributed batch processing |
| **No Real-Time Streaming** | Batch-based only (100s/sec) | Integrate with Kafka Streams or Apache Flink |
| **No Feedback Loop** | Cannot improve rules over time | Add manual review + model retraining pipeline |
| **Limited Features** | Only timestamp-based or account-level | Extend with network analysis, graph features |
| **No Explainability** | Hard to explain alerts to users | Add feature importance and rule explanation |
| **No PII Redaction** | Sensitive data in logs | Implement PII masking before storage |
| **No A/B Testing** | Cannot compare rule versions | Add experiment framework for rule changes |

---

## What This Engine Provides

✅ **Rules-Based Fraud Detection** with hardcoded thresholds  
✅ **Standardized Alert Format** across mobile money and banking  
✅ **Consolidated Logic** replacing duplicate implementations  
✅ **35+ Unit Tests** ensuring correctness  
✅ **Integration Tests** with streaming service  
✅ **Clear Migration Path** from legacy systems  
✅ **Extensible API** for adding new rule types  

❌ **ML Model Included** (graceful degradation only)  
❌ **Real-Time Performance** (batch suitable)  
❌ **Production Monitoring** (alerts only)  
❌ **Rule Explainability** (technical only)  
❌ **Distributed Processing** (single-threaded)  
❌ **Feedback Learning** (static rules)  

---

## Next Steps

1. Deploy consolidated engine as API service
2. Integrate with transaction processing pipelines (dbt + Airflow)
3. Add monitoring/alerting for rule threshold tuning
4. Consolidate dashboards to use unified engine
5. Deprecate legacy fraud modules after successful migration
