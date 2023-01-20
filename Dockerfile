FROM puckel/docker-airflow:1.10.9
#FROM puckel/docker-airflow:1.10.4

ARG AIRFLOW_USER_HOME=/usr/local/airflow
ENV PYTHONPATH=$PYTHONPATH:${AIRFLOW_USER_HOME}

# Python packages required for th Selenium Plugin
USER root

RUN pip install docker && \
    pip install selenium && \
    pip install bs4 && \
    pip install lxml && \
    pip install boto3

RUN groupadd --gid 999 docker \
   && usermod -aG docker airflow 
USER airflow

RUN mkdir downloads
