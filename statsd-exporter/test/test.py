# content of test_module.py
import os
import subprocess
from time import sleep

import pytest
import requests
from prometheus_client.parser import text_string_to_metric_families
from statsd import StatsClient

requests_timeout = 15

# Endpoints are overridable so the suite can run alongside a local dev stack
# that has already claimed 8125/9102 — otherwise the published ports collide
# and the tests silently scrape whichever exporter won the bind, which fails in
# confusing ways. The same knobs let the suite run from inside the compose
# network, where the services answer to their service names.
STATSD_HOST = os.getenv("STATSD_TEST_STATSD_HOST", "127.0.0.1")
STATSD_PORT = int(os.getenv("STATSD_TEST_STATSD_PORT", "8125"))
EXPORTER_HOST = os.getenv("STATSD_TEST_EXPORTER_HOST", "localhost")
EXPORTER_PORT = int(os.getenv("STATSD_TEST_EXPORTER_PORT", "9102"))
EXPORTER_URL = f"http://{EXPORTER_HOST}:{EXPORTER_PORT}"


def _increment_metric(statsd_metric):
    """Send messages to statsd, this is similar to:

    echo "airflow.operator_successes_PythonOperator:1|c" | nc -u -w0
    127.0.0.1 8125
    """
    statsd = StatsClient(host=STATSD_HOST, port=STATSD_PORT, prefix="airflow")
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
    statsd = StatsClient(host=STATSD_HOST, port=STATSD_PORT, prefix="airflow")
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
    statsd = StatsClient(host=STATSD_HOST, port=STATSD_PORT, prefix="airflow")
    statsd.timing(statsd_metric, milliseconds)
    # Avoid race conditions in our testing. After sending the data to
    # statsd, we should allow time for statsd exporter to collect
    # and serve new values
    sleep(0.5)


def _get_metrics():
    response = requests.get(f"{EXPORTER_URL}/metrics", timeout=requests_timeout)
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


def _get_metrics_by_name(name):
    """Every series for ``name``.

    ``_get_metric_by_name`` returns the first match, which is ambiguous when a
    mapping labels one metric name into several series.
    """
    metrics = [metric for metric in _get_metrics() if metric.name == name]
    if not metrics:
        raise Exception(f"Did not find metric {name}")
    return metrics


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
        response = requests.get(EXPORTER_URL, timeout=requests_timeout)
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
        response = requests.get(EXPORTER_URL, timeout=requests_timeout)
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

    def test_operators_labeled_per_operator(self):
        # gen2 keeps the operator name as the label value (`operator: "$1"`),
        # so each operator gets its own series. This is the deliberate
        # difference from gen1, which collapses them all into a literal
        # operator="Value" to keep the Astro UI happy.
        _increment_metric("operator_successes_PythonOperator")
        _increment_metric("operator_successes_BashOperator")

        by_operator = {
            metric.labels["operator"]: metric.value for metric in _get_metrics_by_name("airflow_operator_successes_total")
        }
        assert by_operator.keys() >= {"PythonOperator", "BashOperator"}, f"expected a series per operator, got {by_operator}"
        assert by_operator["PythonOperator"] >= 1
        assert by_operator["BashOperator"] >= 1

    def test_pool_slots_labeled_with_pool_name(self):
        _increment_metric("pool.running_slots.PoolName")
        metric = _get_metric_by_name("airflow_pool_running_slots_total")
        assert metric.labels["pool"] == "PoolName"
        assert metric.value == 1
        _increment_metric("pool.running_slots.PoolName")
        metric = _get_metric_by_name("airflow_pool_running_slots_total")
        assert metric.labels["pool"] == "PoolName"
        assert metric.value == 2

    @pytest.mark.parametrize("sla_metric", ["task_lag", "time_to_first_task"])
    def test_sla_timings_exported_as_seconds_histogram(self, sla_metric):
        # Airflow's Stats.timing converts the seconds-valued timedelta to
        # MILLISECONDS on the wire, but statsd-exporter divides every `|ms`
        # observation by 1000 before handing it to the histogram. The value that
        # actually gets bucketed is therefore in SECONDS, which is what the
        # mapping's buckets (and the _seconds name suffix) are in.
        #
        # This is the guard against "correcting" the buckets to milliseconds on
        # the grounds that the emitter sends ms. With [100 .. 60000] buckets a
        # realistic 650ms timing is observed as 0.65 and lands in the *smallest*
        # bucket, so every observation saturates the entire histogram and it
        # carries no information: le=100 and le=60000 both read 1, and
        # histogram_quantile() pins to the first bucket edge forever. Asserting
        # that the small buckets stay empty fails loudly in that case.
        _timing_metric(f"astro_event_scheduler.sla.{sla_metric}", 650)

        prefix = f"astro_event_scheduler_sla_{sla_metric}_seconds"
        buckets = {}
        sum_value = count_value = None
        for metric in _get_metrics():
            if metric.name == f"{prefix}_bucket":
                buckets[float(metric.labels["le"])] = metric.value
            elif metric.name == f"{prefix}_sum":
                sum_value = metric.value
            elif metric.name == f"{prefix}_count":
                count_value = metric.value

        assert buckets, f"expected a histogram, but found no {prefix}_bucket series"
        finite_buckets = {le: count for le, count in buckets.items() if le != float("inf")}
        # A seconds layout carries the 1s SLA boundary and tops out at 60s.
        assert 1.0 in finite_buckets, f"buckets are not in seconds: {sorted(finite_buckets)}"
        assert max(finite_buckets) == 60.0, f"unexpected bucket ceiling: {sorted(finite_buckets)}"
        # Cumulative histogram: 650ms is observed as 0.65s, so it is > 0.5 and <= 0.75.
        assert finite_buckets[0.1] == 0, (
            f"a 650ms timing saturated the smallest bucket, so {prefix} is bucketed "
            f"in milliseconds, not seconds: {sorted(finite_buckets.items())}"
        )
        assert finite_buckets[0.5] == 0
        assert finite_buckets[0.75] >= 1
        # Sanity on units: sum is ~0.65 (s), not ~650 (ms).
        assert count_value == 1
        assert sum_value is not None and 0.6 <= sum_value <= 0.7, f"expected _sum near 0.65 seconds, got {sum_value}"

    def test_sla_counter_falls_through_to_safety_net(self):
        # The SLA histogram rules pin `match_metric_type: observer` so they only
        # claim timer/distribution events. A counter that happens to share a name
        # with one of them must fall through to the `sla.(.+)` safety-net rule
        # rather than being consumed by the histogram rule, where statsd-exporter
        # would silently drop it with no series and no error in the log.
        _increment_metric("astro_event_scheduler.sla.task_lag")
        metric = _get_metric_by_name("astro_event_scheduler_sla_task_lag_total")
        assert metric.value >= 1


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
