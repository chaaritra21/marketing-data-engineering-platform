CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(150),
    age INTEGER,
    gender VARCHAR(20),
    city VARCHAR(100),
    customer_segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS warehouse.dim_campaign (
    campaign_key SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) UNIQUE NOT NULL,
    campaign_name VARCHAR(150),
    campaign_type VARCHAR(50),
    objective VARCHAR(100),
    start_date DATE,
    end_date DATE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    day INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    year INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS warehouse.fact_campaign_performance (
    performance_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    campaign_key INTEGER NOT NULL,
    channel_key INTEGER NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    spend NUMERIC(12,2) DEFAULT 0,
    revenue NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES warehouse.dim_customer(customer_key),

    CONSTRAINT fk_fact_campaign
        FOREIGN KEY (campaign_key)
        REFERENCES warehouse.dim_campaign(campaign_key),

    CONSTRAINT fk_fact_channel
        FOREIGN KEY (channel_key)
        REFERENCES warehouse.dim_channel(channel_key),

    CONSTRAINT uq_campaign_performance_grain
        UNIQUE (
            date_key,
            customer_key,
            campaign_key,
            channel_key
        )
);