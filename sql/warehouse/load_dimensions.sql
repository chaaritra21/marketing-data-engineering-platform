-- ============================================================
-- LOAD CUSTOMER DIMENSION
-- ============================================================

INSERT INTO warehouse.dim_customer (
    customer_id,
    customer_name,
    age,
    gender,
    city,
    customer_segment
)
SELECT
    'CUST' || LPAD(gs::TEXT, 3, '0'),
    'Customer ' || LPAD(gs::TEXT, 3, '0'),
    20 + (gs % 41),
    CASE
        WHEN gs % 3 = 0 THEN 'Female'
        WHEN gs % 3 = 1 THEN 'Male'
        ELSE 'Other'
    END,
    CASE
        WHEN gs % 5 = 1 THEN 'Gurugram'
        WHEN gs % 5 = 2 THEN 'Delhi'
        WHEN gs % 5 = 3 THEN 'Mumbai'
        WHEN gs % 5 = 4 THEN 'Bengaluru'
        ELSE 'Pune'
    END,
    CASE
        WHEN gs % 3 = 0 THEN 'Premium'
        WHEN gs % 3 = 1 THEN 'Regular'
        ELSE 'At Risk'
    END
FROM generate_series(1, 10) AS gs
ON CONFLICT (customer_id) DO NOTHING;


-- ============================================================
-- LOAD CAMPAIGN DIMENSION
-- ============================================================

INSERT INTO warehouse.dim_campaign (
    campaign_id,
    campaign_name,
    campaign_type,
    objective,
    start_date,
    end_date
)
VALUES
    (
        'CMP001',
        'Summer Sale',
        'Promotion',
        'Increase Sales',
        '2026-09-01',
        '2026-09-07'
    ),
    (
        'CMP002',
        'New User Welcome',
        'Lifecycle',
        'User Activation',
        '2026-09-03',
        '2026-09-10'
    ),
    (
        'CMP003',
        'Weekend Cashback',
        'Promotion',
        'Increase Transactions',
        '2026-09-05',
        '2026-09-30'
    ),
    (
        'CMP004',
        'Win Back Customers',
        'Retention',
        'Reduce Churn',
        '2026-09-08',
        '2026-09-25'
    ),
    (
        'CMP005',
        'Premium Upgrade',
        'Upsell',
        'Increase Customer Value',
        '2026-09-10',
        '2026-09-30'
    )
ON CONFLICT (campaign_id) DO NOTHING;


-- ============================================================
-- LOAD CHANNEL DIMENSION
-- ============================================================

INSERT INTO warehouse.dim_channel (
    channel_name
)
VALUES
    ('Email'),
    ('SMS'),
    ('Push'),
    ('Social'),
    ('Display')
ON CONFLICT (channel_name) DO NOTHING;


-- ============================================================
-- LOAD DATE DIMENSION
-- ============================================================

INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    day,
    month,
    month_name,
    quarter,
    year,
    day_of_week,
    day_name
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d,
    EXTRACT(DAY FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    TO_CHAR(d, 'Month'),
    EXTRACT(QUARTER FROM d)::INTEGER,
    EXTRACT(YEAR FROM d)::INTEGER,
    EXTRACT(ISODOW FROM d)::INTEGER,
    TO_CHAR(d, 'Day')
FROM generate_series(
    DATE '2026-09-01',
    DATE '2026-09-30',
    INTERVAL '1 day'
) AS series(d)
ON CONFLICT (date_key) DO NOTHING;