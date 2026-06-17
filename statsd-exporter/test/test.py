# content of test_module.py
import subprocess
from time import sleep

import pytest
import requests
from prometheus_client.parser import text_string_to_metric_families
from statsd import StatsClient

requests_timeout = 15


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


def _timing_metric(statsd_metric, milliseconds):
    """Send a statsd timer (``|ms``), the way Airflow's Stats.timing does.

    Airflow converts the ``timedelta`` it is given to milliseconds before
    sending, so the event scheduler's seconds-valued SLA timings reach
    statsd-exporter in milliseconds. We mimic that here by sending ms.
    """
    statsd = StatsClient(host="127.0.0.1", port=8125, prefix="airflow")
    statsd.timing(statsd_metric, milliseconds)
    # Avoid race conditions in our testing. After sending the data to
    # statsd, we should allow time for statsd exporter to collect
    # and serve new values
    sleep(0.5)


def _get_metrics():
    response = requests.get("http://localhost:9102/metrics", timeout=requests_timeout)
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
        response = requests.get("http://localhost:9102", timeout=requests_timeout)
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
        response = requests.get("http://localhost:9102", timeout=requests_timeout)
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

    def test_sla_task_lag_exported_as_millisecond_histogram(self):
        # The astro_event_scheduler SLA timings are emitted via Airflow's
        # Stats.timing, which converts the seconds-valued timedelta to
        # MILLISECONDS on the wire. statsd-exporter observes the raw value with
        # no unit conversion, so the mapping's histogram buckets are in ms.
        #
        # A ~650ms observation (a realistic task_lag) must land in a finite ms
        # bucket (le=1000). This is the guard against someone "simplifying" the
        # buckets back to seconds: a seconds config tops out at le=60, has no
        # le=1000 boundary at all, and would dump 650 straight into +Inf.
        _timing_metric("astro_event_scheduler.sla.task_lag", 650)

        buckets = {}
        sum_value = count_value = None
        for metric in _get_metrics():
            if metric.name == "astro_event_scheduler_sla_task_lag_milliseconds_bucket":
                buckets[float(metric.labels["le"])] = metric.value
            elif metric.name == "astro_event_scheduler_sla_task_lag_milliseconds_sum":
                sum_value = metric.value
            elif metric.name == "astro_event_scheduler_sla_task_lag_milliseconds_count":
                count_value = metric.value

        assert buckets, "expected a histogram, but found no _bucket series"
        # A millisecond bucket layout has an le=1000 boundary; a seconds one does not.
        assert 1000.0 in buckets, f"buckets are not in milliseconds: {sorted(buckets)}"
        # Cumulative histogram: 650 is <= 1000 but > 500.
        assert buckets[1000.0] >= 1
        assert buckets.get(500.0, 0) == 0
        # Sanity on units: sum is ~650 (ms), not ~0.65 (s).
        assert count_value is not None and count_value >= 1
        assert sum_value is not None and sum_value >= 100


@pytest.fixture(scope="class")
def statsd_docker_compose():
    subprocess.run(
        "docker compose up --always-recreate-deps --force-recreate --build -d",
        shell=True,
        check=False,
    )
    sleep(1)
    yield
    subprocess.run("docker compose down", shell=True, check=False)


@pytest.fixture(scope="class")
def statsd_docker_compose_gen2():
    subprocess.run(
        "docker compose -f docker-compose-gen2.yaml up --always-recreate-deps --force-recreate --build -d",
        shell=True,
        check=False,
    )
    sleep(1)
    yield
    subprocess.run("docker compose -f docker-compose-gen2.yaml down", shell=True, check=False)
