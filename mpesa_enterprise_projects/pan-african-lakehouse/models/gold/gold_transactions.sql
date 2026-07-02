select
    transaction_id,
    source_system,
    ingestion_date
from {{ ref('silver_transactions') }}
