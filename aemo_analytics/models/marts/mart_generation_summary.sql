{{ config(
    materialized='table',
    schema='MARTS'
) }}

WITH daily AS (
    SELECT * FROM {{ ref('int_generation_daily') }}
),

regions AS (
    SELECT * FROM {{ ref('dim_region') }}
),

joined AS (
    SELECT
        d.date_day,
        d.region,
        r.region_name,
        r.timezone,
        d.avg_demand_mw,
        d.peak_demand_mw,
        d.min_demand_mw,
        d.avg_price_aud_mwh,
        d.max_price_aud_mwh,
        d.min_price_aud_mwh,
        d.interval_count,

        AVG(d.avg_demand_mw) OVER (
            PARTITION BY d.region
            ORDER BY d.date_day
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_avg_demand_mw,

        AVG(d.avg_price_aud_mwh) OVER (
            PARTITION BY d.region
            ORDER BY d.date_day
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7day_avg_price_aud_mwh,

        DATE_TRUNC('month', d.date_day) AS date_month,
        DAYNAME(d.date_day) AS day_of_week

    FROM daily d
    LEFT JOIN regions r ON d.region = r.region_code
)

SELECT * FROM joined