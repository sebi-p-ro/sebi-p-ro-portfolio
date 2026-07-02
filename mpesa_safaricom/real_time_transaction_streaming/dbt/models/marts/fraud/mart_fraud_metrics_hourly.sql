{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['alert_hour'], 'type': 'btree'},
      {'columns': ['severity'], 'type': 'btree'}
    ]
  )
}}

with fraud_alerts as (
  select
    alert_id,
    transaction_id,
    institution,
    detected_type,
    risk_score,
    severity,
    rules_triggered,
    date_trunc('hour', ingestion_timestamp) as alert_hour
  from {{ ref('stg_fraud_alerts') }}
  where ingestion_timestamp >= current_timestamp - interval '7 days'
)

select
  alert_hour,
  severity,
  detected_type,
  count(distinct alert_id) as total_alerts,
  count(distinct transaction_id) as unique_transactions,
  avg(risk_score) as avg_risk_score,
  max(risk_score) as max_risk_score,
  count(case when severity = 'CRITICAL' then 1 end) as critical_count,
  count(case when severity = 'HIGH' then 1 end) as high_count
from fraud_alerts
group by
  alert_hour,
  severity,
  detected_type
order by alert_hour desc
