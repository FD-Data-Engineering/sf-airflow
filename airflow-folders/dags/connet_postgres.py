from datetime import timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago
import airflow

now = datetime.now()
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag_psql = DAG(
    dag_id = "postgresoperator_demo",
    default_args=default_args,
    # schedule_interval='0 0 * * *',
    schedule_interval='@once',	
    dagrun_timeout=timedelta(minutes=60),
    description='use case of psql operator in airflow',
    start_date = airflow.utils.dates.days_ago(1)
)

start = DummyOperator(task_id="start", dag=dag)

create_table_sql_query = """ 
CREATE TABLE employee (id INT NOT NULL, name VARCHAR(250) NOT NULL, dept VARCHAR(250) NOT NULL);
"""
insert_data_sql_query = """
insert into employee (id, name, dept) values(1, 'Prasad','bigdata'),(2, 'Hari','bigdata'),(3, 'Binny','projectmanager'),
(4, 'omair','projectmanager') ;"""

create_table = PostgresOperator(
sql = create_table_sql_query,
task_id = "create_table_task",
postgres_conn_id = "postgres_default",
dag = dag_psql
   )

insert_data = PostgresOperator(
sql = insert_data_sql_query,
task_id = "insert_data_task",
postgres_conn_id = "postgres_default",
dag = dag_psql
    )

end = DummyOperator(task_id="end", dag=dag)  
start >> create_table >> insert_data >> end