from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow import AirflowException
import time
import requests
import json
#from Gamma_Loan_Visualisation import popup_html_ber

###############################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
postgres_driver_jar = "/usr/local/spark/resources/jars/postgresql-9.4.1207.jar"
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
    #api_url="https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications"
    headers = {"Authorization": "Bearer "+access_token}
    dt = jobDetails
    response = requests.post(api_url, json=dt, headers=headers)
    jobResponse = response.json()
    return jobResponse["id"]    


def getApplicationStatus(api_url,access_token):
    #api_url="https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications/"+applicationId+"/state"
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
        dag_id="SF-Gamma-EBA-PILLAR-III", 
        description="This DAG is a sample of integration between Spark and DB. It reads CSV files, load them into a Postgres DB and then read them from the same Postgres DB.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )


start_job_eba = DummyOperator(task_id="start_job_eba", dag=dag)

checkToken = PythonOperator(task_id='fetch_access_token_expiration', python_callable=fetch_access_token_expiration, dag=dag)

job_eba = PythonOperator(task_id='job_eba', python_callable=triggerBatch, op_kwargs={"api_url":"https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications","access_token":Variable.get("Access_Token"), "jobDetails":{"application_details": {      
        "application": "cos://transformedgammadata.Gamma/scripts/v.1.0/EBA_Pillar_III.py",
        "conf": {"spark.hadoop.fs.cos.Gamma.endpoint": "s3.direct.eu-de.cloud-object-storage.appdomain.cloud",
                 "spark.hadoop.fs.cos.Gamma.access.key": "3dbafb4b2fc74197bf8502767a9a73cc",
                 "spark.hadoop.fs.cos.Gamma.secret.key": "5c306426caedaf8782fd4cd8a1cf39e6e46e36e20e885f7a",
                 "spark.app.name": "SF-Gamma-EBA-PILLAR-III"      }   }  }}, dag=dag)

job_eba_status = PythonOperator(task_id='job_eba_status', python_callable=jobCompletionCheck, op_kwargs={"api_url":"https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/2f641c08-2aee-438c-b8a0-eb1738f88c58/spark_applications/{{ task_instance.xcom_pull(task_ids='job_eba') }}/state","access_token":Variable.get("Access_Token")}, dag=dag)   

end_job_eba = DummyOperator(task_id="end_job_eba", dag=dag)

start_job_eba >> checkToken >> job_eba >> job_eba_status >> end_job_eba

