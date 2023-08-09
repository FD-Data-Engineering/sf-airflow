import pytest
from airflow.models import DagBag
from airflow.operators.python import PythonOperator



@pytest.fixture()
def dagbag():
    return DagBag()


def test_dag_loaded(dagbag):
    dag = dagbag.get_dag(dag_id="hellodag")
    assert dagbag.import_errors == {}
    assert dag is not None
    assert len(dag.tasks) == 1

