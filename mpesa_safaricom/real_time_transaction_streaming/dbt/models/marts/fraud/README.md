# Fraud Detection Analytics Models

## Overview

This directory contains dbt models for fraud detection analytics, integrated with the `StreamingFraudDetectionService` that processes real-time transactions through the `ConsolidatedFraudDetectionEngine`.

## Architecture

```
Transaction Stream (Kafka)
        ↓
StreamingFraudDetectionService
        ↓
ConsolidatedFraudDetectionEngine
        ↓
fraud_alerts table
        ↓
dbt Staging & Aggregation
        ↓
Marts (hourly, daily, high-value)
        ↓
Streaming Dashboard
```

## Models

### Staging

- **`stg_fraud_alerts.sql`** — Pass-through of raw fraud_alerts table
  - Source: `raw.fraud_alerts` (Kafka consumer output)
  - Used by: All fraud marts

### Marts

- **`mart_fraud_metrics_hourly.sql`** — Aggregated hourly fraud statistics
  - Granularity: 1 hour × 1 severity × 1 detected_type
  - Purpose: Real-time dashboard and trend monitoring
  - Retention: 7 days

- **`mart_fraud_metrics_daily.sql`** — Aggregated daily fraud statistics
  - Granularity: 1 day × 1 institution × 1 detected_type
  - Purpose: Reporting, trend analysis, performance review
  - Retention: 90 days
  - Includes: Critical/high percentage calculations

- **`mart_fraud_high_value_summary.sql`** — High-severity alerts with details
  - Filter: Severity in (HIGH, CRITICAL)
  - Purpose: Case management, investigative workflows
  - Join: Includes transaction details from stg_mpesa_raw
  - Retention: 30 days

## Integration with Streaming Service

### Step 1: Deploy Fraud Detection Service

```bash
cd mpesa_safaricom/real_time_transaction_streaming/

# Install dependencies (includes fraud_detection_unified)
pip install -r requirements.txt

# Start Kafka consumer for fraud detection
python -m app.services.fraud_detection_service
```

### Step 2: Create fraud_alerts Table

```sql
CREATE TABLE fraud_alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    institution VARCHAR(100) NOT NULL,
    detected_type VARCHAR(50),
    risk_score NUMERIC(5,4),
    severity VARCHAR(20) NOT NULL,
    rules_triggered TEXT,
    detected_timestamp TIMESTAMP,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fraud_alerts_severity ON fraud_alerts(severity);
CREATE INDEX idx_fraud_alerts_transaction ON fraud_alerts(transaction_id);
CREATE INDEX idx_fraud_alerts_timestamp ON fraud_alerts(ingestion_timestamp);
```

### Step 3: Configure dbt sources

In your `dbt_project.yml`:

```yaml
sources:
  - name: raw
    schema: public  # or your warehouse schema
    tables:
      - name: fraud_alerts
```

### Step 4: Run dbt Models

```bash
cd dbt/

# Parse and validate
dbt parse

# Run staging and marts
dbt run --select tag:fraud

# Test data quality
dbt test --select tag:fraud
```

### Step 5: Connect to Dashboard

Update `dashboards/streaming_dashboard.py` to consume fraud metrics:

```python
from sqlalchemy import text

# Query hourly fraud metrics
query = """
SELECT alert_hour, severity, total_alerts, critical_count
FROM marts.mart_fraud_metrics_hourly
WHERE alert_hour > NOW() - INTERVAL '24 hours'
ORDER BY alert_hour DESC
"""

fraud_data = pd.read_sql(text(query), db_engine)
st.bar_chart(fraud_data.set_index('alert_hour'))
```

## Data Quality Tests

Each model includes basic dbt tests:

- `stg_fraud_alerts.alert_id`: unique + not_null
- `mart_fraud_metrics_hourly.alert_hour`: not_null
- `mart_fraud_metrics_daily.alert_date`: not_null + institution not_null

Add custom tests as needed:

```yaml
models:
  - name: mart_fraud_metrics_daily
    columns:
      - name: critical_high_pct
        tests:
          - dbt_utils.expression_is_true:
              expression: "critical_high_pct >= 0 AND critical_high_pct <= 100"
```

## Performance Considerations

- **Hourly mart**: Queries last 7 days (rolling window). Add retention policy in Airflow to purge >7 days.
- **Daily mart**: Queries last 90 days. Archive to cold storage for older data.
- **High-value mart**: Filtered for HIGH+CRITICAL only; suitable for fast retrieval (case management).

## Deployment Checklist

- [ ] `fraud_detection_unified` installed in streaming environment
- [ ] `StreamingFraudDetectionService` consumer deployed and running
- [ ] `fraud_alerts` table created in PostgreSQL/warehouse
- [ ] dbt sources configured pointing to `fraud_alerts` table
- [ ] Models run successfully: `dbt run --select tag:fraud`
- [ ] Tests pass: `dbt test --select tag:fraud`
- [ ] Dashboard updated to query fraud marts
- [ ] Monitoring/alerting configured for HIGH+CRITICAL severity alerts

## Troubleshooting

**Issue**: `fraud_alerts` table empty after service runs
- Check: Is the Kafka consumer running? `ps aux | grep fraud_detection_service`
- Check: Are transactions flowing through Kafka? Monitor consumer lag

**Issue**: dbt models fail with source not found
- Check: Does the `fraud_alerts` table exist? `\d fraud_alerts`
- Check: Is the `raw` schema correct in sources configuration?

**Issue**: Hourly aggregations show zeros
- Check: Are alerts being ingested? `SELECT COUNT(*) FROM fraud_alerts WHERE ingestion_timestamp > NOW() - INTERVAL '1 hour';`

## Future Enhancements

1. **Anomaly Detection**: Detect unusual patterns in fraud rules being triggered
2. **Attribution**: Track which rules are most effective over time
3. **Feedback Loop**: ML model retraining based on analyst case resolutions
4. **Alert Routing**: dbt model to route alerts to appropriate investigation team
5. **SLA Tracking**: Track time-to-resolution for different alert severities
