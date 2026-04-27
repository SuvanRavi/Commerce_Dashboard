WITH source AS (
    SELECT * FROM {{source('ecommerce_raw','users')}}
),

renamed as (
    SELECT
        id AS customer_id,
        email,
        username,
        first_name,
        last_name,
        phone,
        city,
        zipcode,
        ingested_at
    FROM source
    qualify row_number() OVER (
        PARTITION BY id
        ORDER BY ingested_at DESC
    ) = 1
)

SELECT * FROM renamed