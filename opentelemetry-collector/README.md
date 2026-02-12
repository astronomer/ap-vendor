# ap-opentelemetry-collector

Docker image for OpenTelemetry Collector (Contrib), based on [otel/opentelemetry-collector-contrib](https://hub.docker.com/r/otel/opentelemetry-collector-contrib) (see `version.txt` for the base image tag).

## Configs included in the image

- **`/etc/otelcol-contrib/config.yaml`** (default) — OTLP (gRPC/HTTP) in → batch → debug.
- **`/etc/otelcol-contrib/config-gen2.yaml`** — StatsD on 8125 → Airflow metric renames and label extraction (parity with mappings-gen2) → Prometheus on 9102.

The container starts with `--config=/etc/otelcol-contrib/config.yaml` unless you override it (see below).

## Using different configs at runtime

You can switch config in three ways:

### 1. Override the `--config` argument

Use another config that is already inside the image:

```bash
docker run --rm -p 4317:4317 -p 4318:4318 \
  quay.io/astronomer/ap-opentelemetry-collector \
  --config=/etc/otelcol-contrib/config-gen2.yaml
```

Example for Kubernetes: set the container `args` (or `command`/`args`) to `["--config=/etc/otelcol-contrib/config-gen2.yaml"]`.

### 2. Mount your own config file

Mount a host file over the default path so the image’s default `CMD` still works:

```bash
docker run --rm -v /path/on/host/myconfig.yaml:/etc/otelcol-contrib/config.yaml \
  -p 4317:4317 -p 4318:4318 \
  quay.io/astronomer/ap-opentelemetry-collector
```

Or mount to a different path and pass that path to `--config`:

```bash
docker run --rm -v /path/on/host/myconfig.yaml:/config/myconfig.yaml \
  -p 4317:4317 \
  quay.io/astronomer/ap-opentelemetry-collector \
  --config=/config/myconfig.yaml
```

### 3. Config from an environment variable or URL

The collector supports [config providers](https://opentelemetry.io/docs/collector/configuration/#location). You can point `--config` at a URI instead of a file path:

- **Environment variable:** `--config=env:OTEL_CONFIG` (collector reads YAML from the `OTEL_CONFIG` env var).
- **HTTP(S):** `--config=http://example.com/otel.yaml`.

Example with env:

```bash
export OTEL_CONFIG="$(cat myconfig.yaml)"
docker run --rm -e OTEL_CONFIG -p 4317:4317 \
  quay.io/astronomer/ap-opentelemetry-collector \
  --config=env:OTEL_CONFIG
```

You can also pass multiple configs; they are merged:

```bash
docker run --rm ... \
  --config=/etc/otelcol-contrib/config.yaml \
  --config=file:/config/extra.yaml
```

## Config vs statsd-exporter mappings

This image does **not** use the same mapping format as [statsd-exporter](../statsd-exporter/). Statsd-exporter consumes StatsD metrics and applies a YAML mapping file to produce Prometheus metrics with labels.

The OpenTelemetry Collector uses a different model:

- **Receivers** — ingest data (OTLP, StatsD, Prometheus, etc.)
- **Processors** — transform, filter, or enrich (e.g. **transform** processor for renaming metrics or adding attributes)
- **Exporters** — send data to backends (OTLP, Prometheus, debug, etc.)

To rename metrics or add labels in the collector, use the [transform processor](https://opentelemetry.io/docs/collector/configuration/#transform-processor) (OTTLC) in your config. The configs in `include/` are full collector configs (receivers/processors/exporters).

### config-gen2 parity with mappings-gen2

`config-gen2.yaml` aims for parity with [statsd-exporter mappings-gen2.yml](../statsd-exporter/include/mappings-gen2.yml): same allowlist behavior, renamed metric names, and labels (job_name, dag_id, task_id, pool, type, instance, mount_path, le, etc.). Label extraction uses the transform processor in **datapoint** context with **ExtractPatterns** (named capture groups) so that `datapoint.attributes` become Prometheus labels. Pipeline order: **filter/airflow** → **transform/labels** (ExtractPatterns from `metric.name` into datapoint attributes) → **metricstransform** (rename) → **filter/renamed** → batch → Prometheus. **filter/renamed** is a maintained allowlist—update its metric name list when you add new renames or transforms.
