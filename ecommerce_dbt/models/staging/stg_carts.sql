WITH source AS (
    SELECT * FROM {{ source('ecommerce_raw', 'carts') }}
),

renamed AS (
    SELECT
        cart_id,
        user_id AS customer_id,
        date(cast(cart_date AS TIMESTAMP)) AS order_date,
        product_id,
        quantity,
        ingested_at

    FROM source
    qualify row_number() OVER (
        PARTITION BY cart_id, product_id
        ORDER BY ingested_at DESC
    ) = 1
)

SELECT * FROM renamed