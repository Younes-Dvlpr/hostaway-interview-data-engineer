
WITH sales as (

    SELECT * FROM {{ source('ingestion', 'generated_sales_data') }}

),

dim_retailer as (

    SELECT DISTINCT
        RetailerID,
        RetailerName,
        Channel,
        Location
    FROM sales
    ORDER BY RetailerID
)

SELECT * FROM dim_retailer