# Phase 3: Streaming Infrastructure Polish

## Goal

Polish the M-Pesa real-time transaction streaming pipeline to production-grade quality with integrated fraud detection, proper aggregations, and monitoring.

## Current State Assessment

### Existing Strengths ✅
- **Flask/FastAPI webhook receivers** with security headers and input validation
- **Kafka topic architecture** for event streaming (Zookeeper + Kafka 7.5.0)
- **PostgreSQL data warehouse** with health checks
- **dbt staging/mart models** for transaction analytics
- **Grafana dashboards** configured for visualization
- **Docker Compose setup** with proper networking and persistence
- **Airflow DAGs** for orchestration
- **Security components**: HTTPS, secret management, Kubernetes manifests

### Current Gaps 🟡
1. **Fraud Detection Not Integrated**: Streaming pipeline exists but fraud detection is disconnected
2. **Missing Aggregation Models**: No hourly/daily fraud statistics for dashboard consumption
3. **No Streaming Service Wrapper**: Fraud detection engine not embedded in the stream processor
4. **Documentation Gap**: Unclear how to integrate unified fraud detection with existing pipeline
5. **Error Handling**: No dead-letter queue for failed fraud detections
6. **Monitoring**: Limited observability for fraud detection performance

## Phase 3 Objectives

### Objective 1: Integrate Fraud Detection into Stream
Create a streaming fraud detection service that:
- Receives transactions from Kafka
- Scores using ConsolidatedFraudDetectionEngine
- Publishes alerts to fraud_alerts topic
- Maintains audit trail

### Objective 2: Create Fraud Statistics Aggregations
Add dbt models for:
- `marts/mart_fraud_metrics_hourly` — Fraud alerts per hour
- `marts/mart_fraud_metrics_daily` — Fraud patterns per day
- `marts/mart_fraud_high_value_summary` — High-risk transaction summaries
- `marts/mart_fraud_velocity_patterns` — Velocity spike tracking

### Objective 3: Polish Ingestion Layer
- Add proper error handling and retries
- Implement transaction idempotency
- Add schema evolution handling
- Create dead-letter queue topic

### Objective 4: Update Dashboards
- Modify streaming dashboard to show fraud alerts
- Add fraud severity breakdown by type
- Show rule triggers over time
- Add alert routing/escalation indicators

## Implementation Plan

### File Structure
```
mpesa_safaricom/real_time_transaction_streaming/
├── app/
│   ├── services/
│   │   └── fraud_detection_service.py        (NEW)
│   ├── main.py
│   └── config.py
├── dbt/
│   └── models/
│       └── marts/
│           ├── mart_fraud_metrics_hourly.sql  (NEW)
│           ├── mart_fraud_metrics_daily.sql   (NEW)
│           └── mart_fraud_high_value_summary.sql (NEW)
├── dashboards/
│   └── streaming_dashboard.py                 (UPDATE)
└── requirements.txt                           (UPDATE)
```

### Key Tasks

1. **Create fraud_detection_service.py** (Priority 1 — blocks other work)
   - Load ConsolidatedFraudDetectionEngine
   - Consume transactions from Kafka
   - Score and publish fraud alerts
   - Handle errors gracefully

2. **Create dbt fraud aggregation models** (Priority 2)
   - Aggregate fraud alerts to hourly/daily buckets
   - Summarize by fraud type, severity, institution
   - Track rule trigger patterns

3. **Update streaming dashboard** (Priority 3)
   - Add fraud metrics to main view
   - Show alert history and severity trends
   - Add fraud rule breakdown

4. **Add schema evolution** (Priority 4)
   - Document transaction schema versioning
   - Add schema registry integration

## Expected Benefits

- 🟢 Fraud detection becomes real-time rather than batch
- 🟢 Dashboard shows active fraud threats
- 🟢 Rules are configurable via dbt variables (no code redeploy)
- 🟢 Audit trail captured in data warehouse
- 🟢 Fraud metrics exportable for reporting

## Success Criteria

- [ ] `fraud_detection_service.py` successfully processes sample transactions
- [ ] dbt models parse without error and produce correct aggregations
- [ ] Streaming dashboard displays fraud metrics
- [ ] E2E test: Transaction through ingestion → Kafka → fraud engine → warehouse → dashboard
- [ ] Documentation updated with fraud detection integration steps
- [ ] Error handling tested with malformed inputs

## Dependencies

- ✅ fraud_detection_unified/ (Phase 2 — already available)
- ✅ PostgreSQL (streaming project has it)
- ✅ Kafka (streaming project has it)
- ✅ dbt (already set up)

## Risk Mitigation

- **Fraud Engine Failure**: Service catches exceptions, defaults to low-risk, logs to dead-letter queue
- **Schema Mismatch**: Define strict schemas for fraud alerts table
- **Performance**: Fraud scoring runs in parallel consumer threads
- **Backpressure**: Alert batching to avoid overwhelming downstream

## Next Phase Dependency

Phase 4 (test coverage) will verify streaming pipeline with fraud detection through comprehensive integration tests.
