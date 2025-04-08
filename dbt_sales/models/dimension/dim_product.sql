
WITH sales as (

    SELECT * FROM {{ source('ingestion', 'generated_sales_data') }}

),

dim_product as (

    SELECT DISTINCT
        ProductID,
        ProductName,
        Brand,
        Category
    FROM sales
    ORDER BY ProductID

--    example to make fail the test
--    UNION
--
--        SELECT
--            1 AS ProductID,
--            'Laptop' AS ProductName,
--            'BrandA' AS Brand,
--            'Electronics' AS Category;
)

SELECT * FROM dim_product