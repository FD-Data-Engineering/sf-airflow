from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow import AirflowException
import time
import requests
import json

################################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
dtStr = datetime.today().strftime('%Y%m%d')


###############################################
# DAG Definition
###############################################
now = datetime.now()


def fetch_access_token_expiration():
    if Variable.get("Access_Token"):
        counter = 0
        while float(now.timestamp()) > float(Variable.get("Expiration")) and counter<2:
            print("Attempt:"+str(counter))
            close_time=time.time()+ 60
            while time.time()<close_time:
                pass
            counter+=1
        if counter == 2:
            raise ValueError("Token not refreshed")
    else:
        raise ValueError ("Access_Token does not exists!")

#{{ task_instance.xcom_pull(task_ids='Task1') }}
def triggerBatch(api_url,access_token,jobDetails):
    print("trigger bacth job....")
    headers = {"Authorization": "Bearer "+access_token}
    dt = jobDetails
    response = requests.post(api_url, json=dt, headers=headers)
    jobResponse = response.json()
    return jobResponse["id"]    


def getApplicationStatus(api_url,access_token):
    headers = {"Authorization": "Bearer "+access_token}
    response = requests.get(api_url, headers=headers)
    return json.loads(response.content)["state"]
    
def jobCompletionCheck(api_url,access_token):
    appStatus = getApplicationStatus(api_url,access_token)
    while appStatus == "running" or appStatus == "accepted" :
        appStatus = getApplicationStatus(api_url,access_token)

    if appStatus == "failed" or appStatus == "stopped":
        raise ValueError("Job Failed!!!")
    else:
        return True
        

    
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
        dag_id="SF-Airbus-data-process", 
        description="DAG to process airbus data",
        default_args=default_args, 
        schedule_interval=None
    )

start_load_airbus = DummyOperator(task_id="start_load_airbus", dag=dag)

checkToken = PythonOperator(task_id='fetch_access_token_expiration', python_callable=fetch_access_token_expiration, dag=dag)

mergeairbus = PythonOperator(task_id='mergeairbus', python_callable=triggerBatch, op_kwargs={"api_url":"https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications","access_token":Variable.get("Access_Token"), "jobDetails":{"application_details": {      
        "application": "cos://transformedairbusdata.Airbus/scripts/v.1.0/mergeairbus.py",
        "conf": {"spark.hadoop.fs.cos.Airbus.endpoint": "s3.direct.eu-de.cloud-object-storage.appdomain.cloud",
                 "spark.hadoop.fs.cos.Airbus.access.key": "01fc0d80849541eda6515b9d6ea2329b",
                 "spark.hadoop.fs.cos.Airbus.secret.key": "65862b4d74e5183f18f96bed6b44c93f235ea3363bf6d607",
                 "spark.app.name": "SF-Airbus-Merge-data"      }   }  }}, dag=dag)

checkMergeAirbusStatus = PythonOperator(task_id='mergeairbusJobStatus', python_callable=jobCompletionCheck, op_kwargs={"api_url":"https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications/{{ task_instance.xcom_pull(task_ids='mergeairbus') }}/state","access_token":Variable.get("Access_Token")}, dag=dag)   


start_load_airbus >> checkToken >> mergeairbus >> checkMergeAirbusStatus