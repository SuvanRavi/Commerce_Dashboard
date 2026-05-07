WITH source AS (
    SELECT * FROM {{ source('ecommerce_raw', 'users') }}
),

deduped AS (
    SELECT
        id AS customer_id,
        email,
        username,
        first_name,
        last_name,
        phone,
        zipcode,
        ingested_at
    FROM source
    QUALIFY row_number() OVER (
        PARTITION BY id
        ORDER BY ingested_at DESC
    ) = 1
),

randomizing AS (
    SELECT
        *,
        -- Generate a stable number between 0 and 14
        ABS(MOD(FARM_FINGERPRINT(CAST(customer_id AS STRING)), 15)) AS city_index
    FROM deduped
),

final AS (
    SELECT
        customer_id,
        email,
        username,
        first_name,
        last_name,
        phone,
        -- Pick from 15 major US cities
        [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
            'Philadelphia', 'Washington', 'San Diego', 'Dallas', 'Seattle', 
            'Austin', 'Las Vegas', 'San Francisco', 'New Orleans', 'Indianapolis'
        ][OFFSET(city_index)] AS city,
        zipcode,
        ingested_at
    FROM randomizing
)

SELECT * FROM final