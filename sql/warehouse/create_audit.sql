CREATE TABLE IF NOT EXISTS warehouse.etl_audit_log (
    run_id BIGSERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL,
    customer_count INTEGER,
    campaign_count INTEGER,
    channel_count INTEGER,
    date_count INTEGER,
    fact_count INTEGER,
    error_message TEXT
);