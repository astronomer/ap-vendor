# content of test_module.py
import subprocess
from time import sleep

import pytest
import requests
from prometheus_client.parser import text_string_to_metric_families
from statsd import StatsClient


def _increment_metric(statsd_metric):
    """Send messages to statsd, this is similar to:

    echo "airflow.operator_successes_PythonOperator:1|c" | nc -u -w0
    127.0.0.1 8125
    """
    statsd = StatsClient(host="127.0.0.1", port=8125, prefix="airflow")
    statsd.incr(statsd_metric)
    # Avoid race conditions in our testing. After sending the data to
    # statsd, we should allow time for statsd exporter to collect
    # and serve new values
    sleep(0.5)


def _gauge_metric(statsd_metric, value):
    """Send messages to statsd, this is similar to:

    echo "airflow.operator_successes_PythonOperator:1|c" | nc -u -w0
    127.0.0.1 8125
    """
    statsd = StatsClient(host="127.0.0.1", port=8125, prefix="airflow")
    statsd.gauge(statsd_metric, value)
    # Avoid race conditions in our testing. After sending the data to
    # statsd, we should allow time for statsd exporter to collect
    # and serve new values
    sleep(0.5)


def _get_metrics():
    response = requests.get("http://localhost:9102/metrics")
    print(response.text)
    for family in text_string_to_metric_families(response.text):
        for sample in family.samples:
            yield Metric(sample[0], labels=sample[1], value=sample[2])


def _get_metric_by_name(name):
    found_metrics = []
    for metric in _get_metrics():
        if metric.name == name:
            return metric
        found_metrics.append(metric.name)
    raise Exception(f"Did not find metric {name}, only found metrics: {found_metrics}")


class Metric:
    def __str__(self):
        return f"name: {self.name}, labels: {self.labels}, value: {self.value}"

    def __init__(self, name, labels={}, value=None):
        self.name = name
        self.labels = labels
        self.value = value


@pytest.mark.usefixtures("statsd_docker_compose")
class TestGen1:
    def test_server_running(self):
        response = requests.get("http://localhost:9102")
        assert response.status_code == 200

    def test_increment_metric(self):
        _increment_metric("scheduler_heartbeat")
        metric = _get_metric_by_name("airflow_scheduler_heartbeat_total")
        assert metric.value == 1
        _increment_metric("scheduler_heartbeat")
        metric = _get_metric_by_name("airflow_scheduler_heartbeat_total")
        assert metric.value == 2

    def test_operators_conflated_to_single_metric(self):
        _increment_metric("operator_successes_PythonOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.value == 1
        _increment_metric("operator_successes_BashOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.value == 2

    def test_operators_labeled_with_value(self):
        _increment_metric("operator_successes_PythonOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.labels["operator"] == "Value"


@pytest.mark.usefixtures("statsd_docker_compose_gen2")
class TestGen2:
    def test_server_running(self):
        response = requests.get("http://localhost:9102")
        assert response.status_code == 200

    def test_increment_metric(self):
        # scheduler.tasks.starvin
        _increment_metric("scheduler.tasks.starving")
        metric = _get_metric_by_name("airflow_scheduler_tasks_starving_total")
        assert metric.value == 1
        _increment_metric("scheduler.tasks.starving")
        metric = _get_metric_by_name("airflow_scheduler_tasks_starving_total")
        assert metric.value == 2

        # scheduler.tasks.killed_externally
        _increment_metric("scheduler.tasks.killed_externally")
        metric = _get_metric_by_name("airflow_scheduler_tasks_killed_externally_total")
        assert metric.value == 1
        _increment_metric("scheduler.tasks.killed_externally")
        metric = _get_metric_by_name("airflow_scheduler_tasks_killed_externally_total")
        assert metric.value == 2

        # dag_processing.import_errors
        _gauge_metric("dag_processing.import_errors", 2)
        metric = _get_metric_by_name("airflow_dag_processing_import_errors")
        assert metric.value == 2
        _gauge_metric("dag_processing.import_errors", 3)
        metric = _get_metric_by_name("airflow_dag_processing_import_errors")
        assert metric.value == 3

        # dag_processing.total_parse_time
        _gauge_metric("dag_processing.total_parse_time", 20)
        metric = _get_metric_by_name("airflow_dag_processing_total_parse_time")
        assert metric.value == 20
        _gauge_metric("dag_processing.total_parse_time", 30)
        metric = _get_metric_by_name("airflow_dag_processing_total_parse_time")
        assert metric.value == 30

    def test_operators_conflated_to_single_metric(self):
        # operator_successes_PythonOperator
        _increment_metric("operator_successes_PythonOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.value == 1
        _increment_metric("operator_successes_BashOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.value == 2

        # pool.running_slots
        _increment_metric("pool.running_slots.PoolName")
        metric = _get_metric_by_name("airflow_pool_running_slots_total")
        assert metric.labels["pool"] == "PoolName"
        assert metric.value == 1
        _increment_metric("pool.running_slots.PoolName")
        metric = _get_metric_by_name("airflow_pool_running_slots_total")
        assert metric.labels["pool"] == "PoolName"
        assert metric.value == 2

    def test_operators_labeled_with_value(self):
        _increment_metric("operator_successes_PythonOperator")
        metric = _get_metric_by_name("airflow_operator_successes_total")
        assert metric.labels["operator"] == "Value"


@pytest.fixture(scope="class")
def statsd_docker_compose():
    subprocess.run(
        "docker-compose up --always-recreate-deps --force-recreate --build -d",
        shell=True,
    )
    sleep(1)
    yield
    subprocess.run("docker-compose down", shell=True)


@pytest.fixture(scope="class")
def statsd_docker_compose_gen2():
    subprocess.run(
        "docker-compose -f docker-compose-gen2.yaml up --always-recreate-deps --force-recreate --build -d",
        shell=True,
    )
    sleep(1)
    yield
    subprocess.run("docker-compose -f docker-compose-gen2.yaml down", shell=True)
