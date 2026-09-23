-- ============================================================
-- LOAD CAMPAIGN PERFORMANCE FACT
-- Grain:
-- One row = one date × customer × campaign × channel
-- ============================================================

INSERT INTO warehouse.fact_campaign_performance (
    date_key,
    customer_key,
    campaign_key,
    channel_key,
    impressions,
    clicks,
    conversions,
    spend,
    revenue
)
SELECT
    d.date_key,
    c.customer_key,
    cp.campaign_key,
    ch.channel_key,
    i.impressions,
    cl.clicks,
    cv.conversions,
    s.spend,
    r.revenue

FROM warehouse.dim_date d

CROSS JOIN warehouse.dim_customer c

CROSS JOIN warehouse.dim_campaign cp

CROSS JOIN warehouse.dim_channel ch

CROSS JOIN LATERAL (
    SELECT
        (100 + FLOOR(random() * 900))::INTEGER AS impressions
) i

CROSS JOIN LATERAL (
    SELECT
        LEAST(
            i.impressions,
            FLOOR(
                i.impressions * (0.02 + random() * 0.08)
            )
        )::INTEGER AS clicks
) cl

CROSS JOIN LATERAL (
    SELECT
        LEAST(
            cl.clicks,
            FLOOR(
                cl.clicks * (0.05 + random() * 0.20)
            )
        )::INTEGER AS conversions
) cv

CROSS JOIN LATERAL (
    SELECT
        ROUND(
            (5 + random() * 95)::NUMERIC,
            2
        ) AS spend
) s

CROSS JOIN LATERAL (
    SELECT
        ROUND(
            (
                cv.conversions *
                (20 + random() * 80)
            )::NUMERIC,
            2
        ) AS revenue
) r

WHERE cp.start_date <= d.full_date
  AND cp.end_date >= d.full_date

ON CONFLICT (
    date_key,
    customer_key,
    campaign_key,
    channel_key
)
DO NOTHING;