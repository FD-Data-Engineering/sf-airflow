from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import BashOperator,PythonOperator
from datetime import datetime, timedelta

now = datetime.now()
print("Hello_KP")
#FILE = "/usr/local/downloads/NAWS_A2E197.csv"

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
        dag_id="Download_CSV_ValidateRun", 
        description="This DAG downloads a file and validates the file exist then sucess else failure if file doesn't exists",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )
start = DummyOperator(task_id="start", dag=dag)


File_Exist = BashOperator(
    task_id="File_Exist",
    bash_command="echo 'HELLO WORLD'",
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag)  

start >> File_Exist >> end

