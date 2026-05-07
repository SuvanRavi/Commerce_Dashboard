with stg as (
    select * from {{ ref('stg_users')}}
)

select
    customer_id,
    first_name,
    last_name,
    concat(first_name, ' ', last_name) as full_name,
    email,
    city,
    zipcode
from stg