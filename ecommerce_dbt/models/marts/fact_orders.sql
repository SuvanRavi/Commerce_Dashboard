-- Central table where metrics are from
-- Because orders/purchases is primary metric for business.
-- One row per cart-product line item.

with carts as (
    select * from {{ ref('stg_carts')}}
),

products as (
    select * from {{ ref('dim_products')}}
),

joined as (
    select
        c.cart_id as order_id,
        c.customer_id,
        c.order_date,
        c.product_id,
        c.quantity,
        p.product_name,
        p.category,
        p.unit_price,
        p.rating_category,
        p.price_tier,
        c.quantity * p.unit_price as line_total,
        extract(year from c.order_date) as order_year,
        extract(month from c.order_date) as order_month
    from carts c
    left join products p using (product_id)
)

select * from joined