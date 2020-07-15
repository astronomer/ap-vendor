# content of test_module.py
import pytest
import requests
import socket
import subprocess
from time import sleep
from prometheus_client.parser import text_string_to_metric_families
from statsd import StatsClient

def _increment_metric(statsd_metric):
    """
    Send messages to statsd, this is similar to:
    echo "airflow.operator_successes_PythonOperator:1|c" | nc -u -w0 127.0.0.1 8125
    """
    statsd = StatsClient(host='127.0.0.1',
                         port=8125,
                         prefix='airflow')
    statsd.incr(statsd_metric)
    # Avoid race conditions in our testing. After sending the data to
    # statsd, we should allow time for statsd exporter to collect
    # and serve new values
    sleep(0.5)

class Metric():
    def __str__(self):
        return f"name: {self.name}, labels: {self.labels}, value: {self.value}"

    def __init__(self, name, labels={}, value=None):
        self.name = name
        self.labels = labels
        self.value = value

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

def test_server_running():
    response = requests.get("http://localhost:9102")
    assert response.status_code == 200

def test_increment_metric():
    _increment_metric("scheduler_heartbeat")
    metric = _get_metric_by_name("airflow_scheduler_heartbeat_total")
    assert metric.value == 1
    _increment_metric("scheduler_heartbeat")
    metric = _get_metric_by_name("airflow_scheduler_heartbeat_total")
    assert metric.value == 2

def test_operators_conflated_to_single_metric():
    _increment_metric("operator_successes_PythonOperator")
    metric = _get_metric_by_name("airflow_operator_successes_total")
    assert metric.value == 1
    _increment_metric("operator_successes_BashOperator")
    metric = _get_metric_by_name("airflow_operator_successes_total")
    assert metric.value == 2

def test_operators_labeled_with_value():
    _increment_metric("operator_successes_PythonOperator")
    metric = _get_metric_by_name("airflow_operator_successes_total")
    assert metric.labels["operator"] == "Value"

@pytest.fixture(autouse=True, scope='session')
def statsd_docker_compose():
    subprocess.run("docker-compose up --always-recreate-deps --force-recreate --build -d", shell=True)
    sleep(1)
    yield
    subprocess.run("docker-compose down", shell=True)
