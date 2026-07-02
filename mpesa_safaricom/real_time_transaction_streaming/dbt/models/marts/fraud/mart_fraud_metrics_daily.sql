{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['alert_date'], 'type': 'btree'},
      {'columns': ['institution'], 'type': 'btree'}
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
    date(ingestion_timestamp) as alert_date
  from {{ ref('stg_fraud_alerts') }}
  where ingestion_timestamp >= current_timestamp - interval '90 days'
)

select
  alert_date,
  institution,
  detected_type,
  count(distinct alert_id) as total_alerts,
  count(distinct transaction_id) as unique_transactions,
  round(avg(risk_score)::numeric, 4) as avg_risk_score,
  round(max(risk_score)::numeric, 4) as max_risk_score,
  count(case when severity = 'CRITICAL' then 1 end) as critical_alerts,
  count(case when severity = 'HIGH' then 1 end) as high_alerts,
  count(case when severity = 'MEDIUM' then 1 end) as medium_alerts,
  round(
    100.0 * count(case when severity in ('HIGH', 'CRITICAL') then 1 end)
    / nullif(count(*), 0),
    2
  ) as critical_high_pct
from fraud_alerts
group by
  alert_date,
  institution,
  detected_type
order by alert_date desc, critical_high_pct desc
