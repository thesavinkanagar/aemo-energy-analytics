{{ config(
    materialized='view',
    schema='INTERMEDIATE'
) }}

WITH source AS (
    SELECT * FROM {{ ref('stg_generation') }}
),

daily AS (
    SELECT
        DATE_TRUNC('day', settlement_date)  AS date_day,
        region,
        AVG(total_demand_mw)                AS avg_demand_mw,
        MAX(total_demand_mw)                AS peak_demand_mw,
        MIN(total_demand_mw)                AS min_demand_mw,
        AVG(price_aud_mwh)                  AS avg_price_aud_mwh,
        MAX(price_aud_mwh)                  AS max_price_aud_mwh,
        MIN(price_aud_mwh)                  AS min_price_aud_mwh,
        COUNT(*)                            AS interval_count
    FROM source
    GROUP BY 1, 2
)

SELECT * FROM daily