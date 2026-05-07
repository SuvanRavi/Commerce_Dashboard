with order_counts as (
    select
        customer_id,
        count(distinct order_id) as total_orders
    from {{ ref('fact_orders') }}
    group by customer_id
),

classified as (
    select
        customer_id,
        total_orders,
        case
            when total_orders between 1 and 4 then '1-4 orders'
            when total_orders between 5 and 8 then '5-8 orders'
            when total_orders between 9 and 12 then '9-12 orders'
            when total_orders between 13 and 16 then '13-16 orders'
            else '17+ orders'
        end as order_frequency_band
    from order_counts
)

select
    customer_id,
    order_frequency_band,
    total_orders
from classified
group by order_frequency_band, total_orders, customer_id
