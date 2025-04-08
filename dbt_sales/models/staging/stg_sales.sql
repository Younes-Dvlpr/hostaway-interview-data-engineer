WITH source as (

    SELECT
    *
    FROM {{ source('ingestion', 'generated_sales_data') }}

),

renamed as (

    select
        cast(SaleId as bigint)            as sale_id,
        cast(ProductId as bigint)         as product_id,
        cast(RetailerId as bigint)        as retailer_id,
        cast(quantity as integer)         as quantity,
        cast(price as numeric(10, 2))     as price,
        cast("Date" as date)              as sale_date

    from source

)

select *
from renamed
