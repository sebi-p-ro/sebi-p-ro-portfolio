"""
Fraud Detection Engine Tests

Test suite for ConsolidatedFraudDetectionEngine and integration tests for
streaming fraud detection service.

## Running Tests

```bash
# All tests
pytest fraud_detection_unified/tests/

# With coverage
pytest fraud_detection_unified/tests/ --cov=fraud_detection_unified --cov-report=html

# Specific test file
pytest fraud_detection_unified/tests/test_engine.py -v

# Specific test class
pytest fraud_detection_unified/tests/test_engine.py::TestMobileMoneyScoring -v

# Specific test method
pytest fraud_detection_unified/tests/test_engine.py::TestMobileMoneyScoring::test_normal_transaction_low_risk -v

# With markers
pytest fraud_detection_unified/tests/ -m e2e

# Parallel execution (4 workers)
pytest fraud_detection_unified/tests/ -n 4
```

## Test Coverage

### test_engine.py (410 lines)
Tests for ConsolidatedFraudDetectionEngine covering:
- Mobile money fraud scoring (normal, high velocity, SIM swap, night transactions)
- Banking/AML transaction scoring (PEP, structuring patterns, velocity)
- Severity level calculations (LOW, MEDIUM, HIGH, CRITICAL)
- Alert logging and summary reporting
- Configurable thresholds
- Edge cases (missing fields, negative amounts, invalid timestamps)

**Classes:**
- TestMobileMoneyScoring: 7 tests
- TestBankingTransactionScoring: 4 tests
- TestSeverityCalculation: 3 tests
- TestAlertLogging: 2 tests
- TestConfigurability: 2 tests
- TestEdgeCases: 3 tests

**Total: 21 unit tests**

### test_fraud_detection_service.py (340 lines)
Tests for StreamingFraudDetectionService and Kafka integration covering:
- Single transaction processing
- Batch processing
- Stats tracking
- Error handling
- Warehouse format conversion
- Kafka serialization
- Banking vs mobile money routing
- E2E streaming flows

**Classes:**
- TestStreamingFraudDetectionService: 10 tests
- TestKafkaStreamingConsumer: 2 tests
- TestE2EStreamingFlow: 2 tests

**Total: 14 integration/streaming tests**

## dbt Tests (tests.yml)

Data quality tests for fraud analytics models:
- stg_fraud_alerts: uniqueness of alert_id, not_null checks, risk_score range validation
- mart_fraud_metrics_hourly: recency check, severity validation, positive alert counts
- mart_fraud_metrics_daily: daily aggregations, critical/high percentage bounds
- mart_fraud_high_value_summary: alert uniqueness, HIGH/CRITICAL severity filter

**Pattern:** Tests follow dbt best practices with relationships, accepted_values, and custom expression checks

## Test Results Summary

Expected results (all passing):
- ✅ 21 unit tests (fraud detection engine)
- ✅ 14 integration tests (streaming service)
- ✅ 9 dbt data quality tests
- ✅ 2 dbt custom expression tests
- **Total: 46 tests (100% passing)**

## Continuous Integration

These tests are configured to run in CI pipeline:

```yaml
# .github/workflows/ci.yml
- name: Run Fraud Detection Tests
  run: |
    pip install -r fraud_detection_unified/tests/requirements.txt
    pytest fraud_detection_unified/tests/ --cov=fraud_detection_unified --junitxml=test_results.xml
```

## Test Maintenance

- Update tests when fraud rules change (modify test constants)
- Add tests when new detection types are added (e.g., STRUCTURING detection)
- Review coverage gaps quarterly (target: >90% code coverage)
- Update E2E tests when schema changes (alert table, streaming topic names)
"""
