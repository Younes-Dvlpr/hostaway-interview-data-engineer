# 🛠️ Installation
Requirements :
- Docker
- Python ≥ 3.11
- Poetry

# 🚀  Run Project

-   ```bash
    poetry lock && poetry install
    ```
-   ```bash
    docker-compose up -d
    ```
- Trigger the DAG in Airflow server ([http://localhost:8080](http://localhost:8080)) with admin:admin credentials.
- Run the following command to run the dbt project:
```bash
  cd dbt_sales
  dbt deps
  dbt run
```


## 🚀 Pipeline Overview

### 🧼 Part 1 — Data Ingestion & Cleaning

The script `main.py` performs the following:

1. **CSV Reading & Merging**
    - Reads one or multiple CSV files into a `pandas.DataFrame`.
    - Performs an **upsert** using a custom function `upsert_csv_data_into_dataframe()` based on a primary key (
      `SaleID`).

2. **Data Cleaning**
    - Handles missing values (`fillna`) and 'None' values
    - Removes duplicate records
    - Cleans inconsistent values (e.g. price format, empty product IDs)
    - Converts data types (e.g. `Date`, `Price`, `ProductID`)

3. **Export**
    - Outputs a cleaned CSV file at:  
      `/opt/airflow/dags/data/clean_sales_data.csv`

---

### 🛢️ Part 2 — PostgreSQL Integration

PostgreSQL is provisioned in the `docker-compose.yml`. The SQL script does:

- Creates the schema `ingestion`
- Creates the table `generated_sales_data`
- Loads data using the fast `COPY FROM` SQL command
- Adds indexes on key columns:
    - `ProductID`, `ProductName`, `Brand`, `RetailerID`

> Table schema includes a `"Date"` column with proper quoting to avoid reserved word issues.

> For the "Date" column, if the table becomes too big, we can also suggest use partitioning on it, but it implies to
> create a new table and then migrate the data into it.
> Otherwise, we can just index it if is used often in WHERE clauses.
---

### 🌬️ Part 3 — Airflow DAG Execution

The modified docker-compose.yml is creating an Airflow server accessible

📍 Access Airflow UI: [http://localhost:8080](http://localhost:8080)  
🧑 Credentials: `admin` / `admin`

The DAG `Hostaway_interview_DAG` runs:

1. `main.py` to clean the raw sales data
2. The SQL script described in Part 2

To inspect and check results in PostgreSQL (Docker container):

```bash
docker exec -it postgres psql -U postgres -d sales
# Then run:
SELECT * FROM ingestion.generated_sales_data;
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'generated_sales_data';
\d ingestion.generated_sales_data
```

### 🧪 Part 4 — DBT

#### 🔗 Source Tables

### `ingestion.generated_sales_data`

- **Database**: `sales`
- **Schema**: `ingestion`
- This is the raw source table containing all sales data.
- Used by staging and dimensional models.

---

#### 🏗️ Staging Models

### `stg_sales`

> Sales data with essential information only (only figures) and renamed column

#### 📐 Dimension Models

### `dim_product`

> Dimension table for product information

Constructed from distinct values of `generated_sales_data`, representing product-level metadata.

#### Columns

| Column      | Description                    |
|-------------|--------------------------------|
| ProductId   | The primary key for this table |
| ProductName | The name of the product        |
| Brand       | The brand of the product       |
| Category    | The category of the product    |

**Test**: Must be unique on the combination of  
`ProductId`, `ProductName`, `Brand`, `Category`.

---

### `dim_retailer`

> Dimension table for retailer information

Constructed from distinct values of `generated_sales_data`, representing retailer-level metadata.

#### Columns

| Column       | Description                                         |
|--------------|-----------------------------------------------------|
| RetailerId   | The primary key for this table                      |
| RetailerName | The name of the retailer                            |
| Channel      | The channel of the retailer (e.g., online, offline) |
| Location     | The location of the retailer                        |

**Test**: Must be unique on the combination of  
`RetailerId`, `RetailerName`, `Channel`, `Location`.

---

#### 🧪 Summary of Tests

| Model          | Test Type                                 | Columns                                             |
|----------------|-------------------------------------------|-----------------------------------------------------|
| `dim_product`  | `dbt_utils.unique_combination_of_columns` | `ProductId`, `ProductName`, `Brand`, `Category`     |
| `dim_retailer` | `dbt_utils.unique_combination_of_columns` | `RetailerId`, `RetailerName`, `Channel`, `Location` |

