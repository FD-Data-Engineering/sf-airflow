from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hellodag():
    print('Hello from IBM Cloud Airflow')

with DAG(dag_id= 'hellodag',
         start_date= datetime(2023,2,10),
         schedule_interval='*/1 * * * *',
         catchup=False) as dag:
         task1 = PythonOperator(task_id ='hellodag',
         python_callable=hellodag)
         
hellodag
