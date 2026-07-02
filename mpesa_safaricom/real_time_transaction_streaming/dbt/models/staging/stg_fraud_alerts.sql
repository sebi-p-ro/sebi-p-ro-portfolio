{{
  config(
    materialized='ephemeral'
  )
}}

-- Source model for fraud alerts table
-- This model references the raw fraud_alerts table populated by the
-- streaming_fraud_detection_service from the Kafka consumer.
--
-- Expected table schema:
--   alert_id VARCHAR(255) PRIMARY KEY
--   transaction_id VARCHAR(255)
--   institution VARCHAR(100)
--   detected_type VARCHAR(50)
--   risk_score FLOAT
--   severity VARCHAR(20)
--   rules_triggered TEXT
--   detected_timestamp TIMESTAMP
--   ingestion_timestamp TIMESTAMP

select
  alert_id,
  transaction_id,
  institution,
  detected_type,
  risk_score,
  severity,
  rules_triggered,
  detected_timestamp,
  ingestion_timestamp
from {{ source('raw', 'fraud_alerts') }}
