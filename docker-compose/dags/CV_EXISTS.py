from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

now = datetime.now()
FILE = "/usr/local/airflow/downloads/NAWS_A2E197.csv"

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

Download_CSV = BashOperator(
    task_id="Download_CSV",
    bash_command="wget https://www.dol.gov/sites/dolgov/files/ETA/naws/pdfs/NAWS_A2E197.csv -O /usr/local/airflow/downloads/NAWS_A2E197.csv",
    dag=dag,
)

File_Exist = BashOperator(
    task_id="File_Exist",
    bash_command="test -f $FILE && echo '$FILE exists.' || echo '$FILE does not exist.'",
    dag=dag,
)

end = DummyOperator(task_id="end", dag=dag)  

start >> Download_CSV >> File_Exist >> end
