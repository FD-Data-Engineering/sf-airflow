from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print('Hello from IBM Cloud Airflow')

with DAG(dag_id= 'hello',
         start_date= datetime(2023,2,10),
         schedule_interval='@hourly',
         catchup=False) as dag:
         task1 = PythonOperator(task_id ='hello',
         python_callable=hello)
         
hello
