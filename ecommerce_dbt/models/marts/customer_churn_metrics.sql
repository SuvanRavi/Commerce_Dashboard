-- For each month, counts how many customers placed their first ever order

with customer_first_order as (
    -- find the first order date for every customer across all time
    select
        customer_id,
        min(order_date) as first_order_date
    from {{ ref('fact_orders') }}
    group by customer_id
),

orders_with_type as (
    select
        f.customer_id,
        f.order_date,
        date_trunc(f.order_date, month) as order_month,
        date_trunc(c.first_order_date, month) as first_order_month,

        case
            when date_trunc(f.order_date, month)
               = date_trunc(c.first_order_date, month)
            then 'New'
            else 'Returning'
        end as customer_type

    from {{ ref('fact_orders') }} f
    left join customer_first_order c using (customer_id)
),

-- deduplicate: one row per customer per month per type
-- (a customer can only be new or returning in a given month, not both)
deduplicated as (
    select distinct
        customer_id,
        order_month,
        customer_type
    from orders_with_type
)

select
    order_month,
    customer_type,
    count(distinct customer_id) as num_customers
from deduplicated
group by order_month, customer_type
order by order_month, customer_type