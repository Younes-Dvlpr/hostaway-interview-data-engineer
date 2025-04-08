import logging
from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
from airflow import settings
from airflow.models import Connection


def create_conn(conn_id, conn_type, host, login, pwd, port, desc):
    conn = Connection(conn_id=conn_id,
                      conn_type=conn_type,
                      host=host,
                      login=login,
                      password=pwd,
                      port=port,
                      description=desc)
    session = settings.Session()
    conn_name = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()

    if str(conn_name) == str(conn.conn_id):
        logging.warning(f"Connection {conn.conn_id} already exists")
        return None

    session.add(conn)
    session.commit()
    logging.info(Connection.log_info(conn))
    logging.info(f'Connection {conn_id} is created')
    return conn


default_args = {
    'owner': 'airflow',
    'start_date': datetime.today(),
    'catchup': False
}

with DAG('Hostaway_interview_DAG', default_args=default_args, schedule_interval=None):
    run_python_script = BashOperator(
        task_id='python_data_ingestion_and_processing',
        bash_command='python3 /opt/airflow/dags/main.py'
    )

    with open('/opt/airflow/dags/database_integration.sql', 'r') as f:
        database_integration_sql = f.read()

    database_integration = PostgresOperator(
        task_id='query_postgres',
        postgres_conn_id='POSTGRES_SALES', # cf. AIRFLOW_CONN_POSTGRES_SALES environment variable in docker-compose.yml
        sql=database_integration_sql
    )

    run_python_script >> database_integration
