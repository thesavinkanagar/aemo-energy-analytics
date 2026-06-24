{{ config(
    materialized='view',
    schema='STAGING'
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'RAW_GENERATION') }}
),

renamed AS (
    SELECT
        REGION                              AS region,
        TO_TIMESTAMP_NTZ(SETTLEMENTDATE)    AS settlement_date,
        TOTALDEMAND                         AS total_demand_mw,
        RRP                                 AS price_aud_mwh,
        PERIODTYPE                          AS period_type
    FROM source
    WHERE
        TOTALDEMAND IS NOT NULL
        AND RRP IS NOT NULL
        AND SETTLEMENTDATE IS NOT NULL
)

SELECT * FROM renamed