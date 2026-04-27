WITH source AS (
    SELECT * FROM {{source('ecommerce_raw', 'products')}}
),

renamed AS (
    SELECT
        id AS product_id,
        title AS product_name,
        price AS unit_price,
        category, 
        description,
        rating_rate,
        rating_count,
        ingested_at
    FROM source
    qualify row_number() OVER (
        PARTITION BY id
        ORDER BY ingested_at DESC
    ) = 1
)

SELECT * FROM renamed