#!/bin/bash

airflow_root=`pwd`
# pod_name=$(oc get pods --selector io.kompose.service=scheduler --output=name)
pod_name=$(oc get pods --selector io.kompose.service=scheduler --output=name | sed -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//')
reponame="https://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@github.com/FD-Data-Engineering/sf-airflow.git"
airflow_dir="sf-airflow/docker-compose"
git_dir=git
pod_dest="../../../"

oc exec $pod_name bash -c "echo $pod_name && \
        mkdir git && \
        cd git && \
        git init && \
        git config credential.helper store && \
        git clone $reponame && \
        cd $airflow_dir && \
        cp -r dags $pod_dest && \
        cd $airflow_root && \
airflow scheduler -D "

