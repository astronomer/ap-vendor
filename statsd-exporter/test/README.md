# Testing Statsd-exporter

This test scaffolding will bring up statsd-exporter and statsd with docker compose, hooking them up together. The component testing sends metrics to statsd to act like Airflow.

## Play around with it

In this directory, you can run

```
docker-compose up
```

Then, you can view the available metrics http://localhost:9102

You can add a new metric to statsd

```
echo "airflow.operator_successes_PythonOperator:1|c" | nc -u -w0 127.0.0.1 8125
```

Then refresh your browser, you can find a metric:

```
airflow_operator_successes 1
```

## Run the component testing

This basically will do the same thing as above in the setup py test fixture, then tear it down after it's done running the tests. The tests send metrics to statsd, then make assertions about the behavior of statsd-exporter. This serves well to isolate the behavior of statsd-exporter and its configuration without involving Kubernetes, Airflow, and so forth.

```
/bin/bash setup-test-env.sh
source ./venv/bin/activate
pytest ./test.py
```
