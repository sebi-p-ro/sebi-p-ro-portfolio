{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['severity'], 'type': 'btree'},
      {'columns': ['transaction_id'], 'type': 'btree'}
    ]
  )
}}

with fraud_alerts as (
  select
    fa.alert_id,
    fa.transaction_id,
    fa.institution,
    fa.detected_type,
    fa.risk_score,
    fa.severity,
    fa.rules_triggered,
    fa.ingestion_timestamp,
    st.amount,
    st.velocity_60s,
    st.account_reference
  from {{ ref('stg_fraud_alerts') }} fa
  left join {{ ref('stg_mpesa_raw') }} st
    on fa.transaction_id = st.transaction_id
  where fa.severity in ('HIGH', 'CRITICAL')
    and fa.ingestion_timestamp >= current_timestamp - interval '30 days'
)

select
  alert_id,
  transaction_id,
  institution,
  detected_type,
  round(risk_score::numeric, 4) as risk_score,
  severity,
  rules_triggered,
  amount,
  velocity_60s,
  account_reference,
  ingestion_timestamp,
  current_timestamp as computed_at
from fraud_alerts
order by
  risk_score desc,
  ingestion_timestamp desc
