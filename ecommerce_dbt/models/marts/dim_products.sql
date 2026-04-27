with stg as (
    select * from {{ ref('stg_products')}}
)

select
    product_id,
    product_name,
    category,
    unit_price,
    rating_rate,
    rating_count,

    case
        when rating_rate >= 4.5 then 'Excellent'
        when rating_rate >= 3.5 then 'Good'
        when rating_rate >= 2.5 then 'Average'
        else 'Poor'
    end as rating_category,

    case
        when unit_price < 20  then 'Budget'
        when unit_price < 100 then 'Mid-range'
        else 'Premium'
    end as price_tier
    
from stg