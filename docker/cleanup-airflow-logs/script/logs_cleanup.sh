#!/bin/bash

pod_name=$(oc get pods --selector io.kompose.service=scheduler --output=name | sed -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//' -e 's/^[[pod/]]*//')
date=$(date --date "-1 days" '+%Y-%m-%d')

oc exec $pod_name -- bash -c '
        echo "Establishing connection to '$pod_name'"
        echo '$date'
        ls -l /usr/local/airflow/logs/scheduler/'$date'
        echo "deleting logs in '$date' dir"
        rm -rf /usr/local/airflow/logs/scheduler/'$date'
'
