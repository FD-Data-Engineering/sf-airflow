from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

now = datetime.now()
print("File Downloaded")
#FILE = "/usr/local/downloads/NAWS_A2E197.csv"
#data_path = "C:\Users\pgugulla\prometheus"
data_path = "/usr/local/airflow/airflow-scheduler.err"
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
        dag_id="Download_file_from_local", 
        description="This DAG downloads a file from local and then sucess else failure if file doesn't exists",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )
start = DummyOperator(task_id="start", dag=dag)


File_Download = BashOperator(
    task_id="Download_File",
    bash_command="curl --retry 5 - /usr/local/airflow/airflow-scheduler.err",
    dag=dag
)

end = DummyOperator(task_id="end", dag=dag)  

start >> File_Download >> end
#testing 