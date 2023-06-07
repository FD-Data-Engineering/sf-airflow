from datetime import timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
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

dag = DAG(
    dag_id = "alter_table",
    default_args=default_args,
    # schedule_interval='0 0 * * *',
    schedule_interval='@once',	
    dagrun_timeout=timedelta(minutes=60),
    description='use case of psql operator in airflow',
    start_date = airflow.utils.dates.days_ago(1)
)

start = DummyOperator(task_id="start", dag=dag)

alter_table_sql_query = """ 
ALTER TABLE employee ADD COLUMN address VARCHAR(250) NOT NULL);
"""

alter_table = PostgresOperator(
sql = alter_table_sql_query,
task_id = "alter_table_task",
postgres_conn_id = "postgres_default",
dag = dag
   )

end = DummyOperator(task_id="end", dag=dag)  
start >> alter_table >> end
