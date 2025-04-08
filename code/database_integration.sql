CREATE SCHEMA ingestion;

CREATE TABLE IF NOT EXISTS ingestion.generated_sales_data (
    SaleID SERIAL PRIMARY KEY,
    ProductID INT NOT NULL,
    ProductName TEXT NOT NULL,
    Brand TEXT NOT NULL,
    Category TEXT NOT NULL,
    RetailerID INT NOT NULL,
    RetailerName TEXT NOT NULL,
    Channel TEXT NOT NULL,
    Location TEXT NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    "Date" DATE NOT NULL
);

CREATE INDEX idx_productid ON ingestion.generated_sales_data(ProductID); -- Foreign Key
CREATE INDEX idx_productname ON ingestion.generated_sales_data(ProductName); -- Probably often used
CREATE INDEX idx_brand ON ingestion.generated_sales_data(Brand); -- Probably often used
-- CREATE INDEX idx_date ON ingestion.generated_sales_data(Date); Optional

COPY ingestion.generated_sales_data(SaleID, ProductID, ProductName, Brand, Category, RetailerID, RetailerName, Channel, Location, Quantity, Price, "Date")
FROM '/code/data/clean_sales_data.csv'
DELIMITER ';'
CSV HEADER;
