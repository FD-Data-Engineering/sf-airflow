#!/bin/bash

airflow_root=`pwd`
pod_name=$(oc get pods --selector io.kompose.service=scheduler --output=name)
reponame="https://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@github.com/FD-Data-Engineering/sf-airflow.git"
airflow_dir="sf-airflow/docker-compose"
git_dir=git
pod_dest="../../../"

for podName in $pod_name
do
    echo "Establishing connection to" $podName
    oc rsh $podName
    echo "Successfully established connection to" $podName
    if [ ! -d "$git_dir" ] ; then
        echo $git_dir "does not exist in $airflow_root... I am creating it..."
        mkdir git
        cd git
        git init
        git config credential.helper store
        git clone $reponame
        cd $airflow_dir
        cp -r dags $pod_dest
        cd $airflow_root
        airflow scheduler -D
        
    else
        cd git
        cd $airflow_dir
        git config credential.helper store
        git pull $reponame
        cp -r dags $pod_dest
        cd $airflow_root
        airflow scheduler -D
    fi
done

if [[ $? -ne 0 ]]
then
    echo "The Airflow Dags Sync resulted in errors. Please review the logs above."
fi
