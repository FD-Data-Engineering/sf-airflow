#!/bin/bash

airflow_root=`pwd`
pod_name=$(oc get pods --selector io.kompose.service=scheduler --output=name | sed -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//')
reponame="xxxxx@github.com/FD-Data-Engineering/sf-airflow.git"
airflow_dir="sf-airflow/airflow-folders"
git_dir=git
pod_dest="../../../"

oc exec $pod_name -- bash -c '
        echo "Establishing connection to '$pod_name'"
        rm -rf '$git_dir' && mkdir git
        echo "Created '$git_dir' in '$airflow_root'..."
        cd git
        git init
        git config credential.helper store
        git clone '$reponame'
        cd '$airflow_dir'
        cp -r dags '$pod_dest'
        echo "Airflow Dags have now been updated"
        cd '$airflow_root'
        echo "Cleaning up Airflow"
        find '$airflow_root'/logs/scheduler -type f -mtime +1 -delete
airflow scheduler -D '
