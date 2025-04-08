import csv
from io import StringIO
import pandas as pd


def upsert_csv_data_into_dataframe(_df: pd.DataFrame, file_path: str, index_column: str) -> pd.DataFrame:
    # Load new data in a tmp DataFrame
    tmp_df = pd.read_csv(file_path).set_index(index_column)

    # Concat new DataFrame with the input one only if the index is not present (INSERT)
    if not _df.empty:
        _df = pd.concat([tmp_df[~tmp_df.index.isin(_df.index)], _df])
    else:
        _df = tmp_df.copy()

    # (UPSERT)
    _df.update(tmp_df)

    return _df


if __name__ == '__main__':
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 2000)

    ####### PART 1 ######
    dtypes = {
        "ProductID": "int64",
        "ProductName": "string",
        "Brand": "string",
        "Category": "string",
        "RetailerID": "int64",
        "RetailerName": "string",
        "Channel": "string",
        "Location": "string",
        "Quantity": "int64",
        "Price": "float64",
        "Date": "datetime64[ns]"
    }
    index_column_name = "SaleID"
    columns = ["SaleID", "ProductID", "ProductName", "Brand", "Category", "RetailerID", "RetailerName", "Channel",
               "Location", "Quantity", "Price", "Date"]
    init_df = pd.DataFrame(columns=columns).set_index(index_column_name)

    print("-------------------- 1st load --------------------")
    df = upsert_csv_data_into_dataframe(init_df, "/opt/airflow/dags/data/generated_sales_data.csv", index_column_name)
    # print(df)

    print("-------------------- 2nd load --------------------")
    df = upsert_csv_data_into_dataframe(df, "/opt/airflow/dags/data/generated_sales_data_2.csv", index_column_name)
    # print(df)

    # print("Get info")
    # print(df)

    # Identify duplicate rows
    print("-------------------- Get duplicates --------------------")
    df_duplicates = df[df.duplicated(keep="first")]
    # print(df_duplicates.info())
    # print(df_duplicates)

    # Remove duplicate rows
    print("-------------------- Get info after drop_duplicates --------------------")
    df.drop_duplicates(inplace=True)
    # print(df.info())
    # print(df)

    # Clean Columns
    print("-------------------- Clean columns --------------------")
    for col in df.columns:
        print(f"Column: {col} : {df[col].unique()}")

    print("-------------------- Clean Location --------------------")
    df.Location = df.Location.fillna('UNKNOWN')
    df.loc[df.Location == "None", "Location"] = 'UNKNOWN'
    # print(df.info())
    # print(df)

    print("-------------------- Clean ProductId --------------------")
    ### ProductId cleaning
    print(df[df.ProductID == " "])
    Blender = df[(df.ProductName == "Blender")]
    print(Blender.nunique())
    print(Blender.ProductID.unique())
    # Now we are sure that if ProductName = "Blender" then ProductID = 5
    df.loc[df.ProductName == "Blender", "ProductID"] = 5
    print(df[df.ProductID == " "])
    print(df.loc[1001])

    print("-------------------- Clean Price --------------------")
    df.Price = df.Price.str.replace('USD', '')
    df.Price = df.Price.fillna('0')

    print("-------------------- Clean Date --------------------")
    df.Date = df.Date.str.replace('/', '-')

    print("-------------------- After column cleaning --------------------")
    for col in df.columns:
        print(f"Column: {col} : {df[col].unique()}")

    print(df.dtypes)
    df = df.astype(dtypes)
    df.index.astype('int64')
    print(df)
    print(df.dtypes)

    df.to_csv("/opt/airflow/dags/data/clean_sales_data.csv", sep=';', encoding='utf-8', index=True, header=True)

    ####### PART 2 & 3 ######

    # The modified docker-compose.yml is creating an Airflow server accessible on the localhost:8080. Login with admin:admin creds.
    # Then, trigger the DAG "Hostaway_interview_DAG" which will run the main.py script and the SQL script.
    # The SQL script is creating a table "generated_sales_data" in the PostgreSQL database and inserting the data from the clean_sales_data.csv file into it.
    # To check the result in Postgres container in interactive mode :
    # - docker exec -it postgres psql -U postgres -d sales
    # - SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'generated_sales_data';
    # - SELECT * FROM ingestion.generated_sales_data;
    # - \d ingestion.generated_sales_data

    # For indexing, it generally depends on the use case. We should ask the users about the queries they will run on this table.
    # But we can suggest to index : ProductID (foreign key), RetailerID (foreign key), ProductName and Brand because they should be used quite often in WHERE clauses.
    # For the Date column, if the table becomes too big, we can also suggest use partitioning on it, but it implies to create a new table and then migrate the data into it.
    # Otherwise, we can just index it if is used often in WHERE clauses.

    ####### PART 4 ######
    # dbt init --skip-profile-setup --profiles-dir $PWD dbt_sales
    # cd dbt_sales
    # dbt run
