from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import json

now = datetime.now()


def generate_access_token():
    api_url = "https://iam.cloud.ibm.com/identity/token"
    dt = "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=CcZzswuM7FSjGEJ_fdmnL47OwD401XWpqfwC5jYtBnV8"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(api_url, data=dt, headers=headers)
    tokenJson = response.json()
    Access_Token = tokenJson["access_token"]
    Expiration = tokenJson["expiration"]

    Variable.set("Access_Token", Access_Token)
    Variable.set("Expiration", Expiration)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "schedule_interval": '@hourly',
}

dag = DAG(
        dag_id="Set_variable", 
        description="This DAG is used to set variables in airflow.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )
 
start = DummyOperator(task_id="start", dag=dag)
python_task = PythonOperator(task_id='generate_access_token', python_callable=generate_access_token, dag=dag)

start >> python_task