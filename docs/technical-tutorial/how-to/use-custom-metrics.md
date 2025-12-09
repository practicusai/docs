---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Using Custom Observability Metrics

Practicus AI’s model hosting and app hosting system allows you to create and track custom Observability metrics via Prometheus or another time-series database. Follow the steps below to begin publishing your own metrics.

## Step 1) Enable Observability

Verify with your administrator that the model hosting deployment or app hosting deployment setting you plan to use has observability enabled. If not, an admin can open the Practicus AI Admin Console, select the relevant model deployment or app deployment setting and enable it.

## Step 2) For model hosting, modify `model.py`

Initialize Prometheus counters, histograms, etc. as usual, and then update your metrics accordingly. An example is shown below.

```python
# model.py

# ... your existing imports
from prometheus_client import Counter, REGISTRY

my_counter = None


async def init(*args, **kwargs):
    # ... your existing model init code

    global my_counter

    metric_name = "my_test_counter"
    try:
        my_counter = Counter(
            name=metric_name, documentation="My test counter", labelnames=["my_first_dimension", "my_second_dimension"]
        )
    except ValueError:
        # Metric is already defined; retrieve it from the registry
        my_counter = REGISTRY._names_to_collectors.get(metric_name)
        if not my_counter:
            raise  # Something else went wrong


async def predict(df, *args, **kwargs):
    # ... your existing prediction code

    # Increment the counter for the chosen labels
    my_counter.labels(
        my_first_dimension="abc",
        my_second_dimension="xyz",
    ).inc()

    # ... your existing code returning prediction
```

## Step 2) For App Hosting, modify API .py files

You can select any api .py file and initialize Prometheus counters, histograms, etc. as usual, and then update your metrics accordingly. An example is shown below.

```python
# apis/some_api_method.py

# ... your existing imports
from prometheus_client import Counter, REGISTRY
import practicuscore as prt

my_counter = None


def init_counter():
    global my_counter

    metric_name = "my_test_counter"
    try:
        my_counter = Counter(
            name=metric_name, documentation="My test counter", labelnames=["my_first_dimension", "my_second_dimension"]
        )
    except ValueError:
        # Metric is already defined; retrieve it from the registry
        my_counter = REGISTRY._names_to_collectors.get(metric_name)
        if not my_counter:
            raise  # Something else went wrong


def increment_my_counter():
    if not my_counter:
        init_counter()

    # Increment the counter for the chosen labels
    my_counter.labels(
        my_first_dimension="abc",
        my_second_dimension="xyz",
    ).inc()


@prt.apps.api("/some-api-method")
async def run(payload: SomePayloadRequest, **kwargs):
    # ... api code

    # observe any metric
    increment_my_counter()

    # ... your existing code returning api result
```

### Note on Metric Exporters

Prometheus is a **pull-based** monitoring system, which means it regularly scrapes endpoints for metrics rather than having metrics pushed to it. To accommodate this, you can use a **Practicus AI** application as a centralized **Metric Exporter** for your other systems outside of Practicus AI.

In practice, you would:
1. **Build a minimal Practicus AI app** with no UI (i.e., no `Home.py`), focusing solely on exposing API endpoints.
2. **Define metric-specific endpoints**, for example:
   - `increase_counter_x` — increments a particular counter.
   - `observe_histogram_y` — records a value for a given histogram.

And the Prometheus-compatible `/metrics` endpoint would be automatically created, assuming your admin enabled observability for app hosting setting you use.

This design pattern allows external systems to call your Practicus AI app to update metrics, while Prometheus simply pulls the metrics from one central place.

**Important Considerations**:
- **Single Replica**: Ensure your app deployment setting uses a single replica (1 Kubernetes pod). This makes your metrics consistent and avoids synchronization issues.
- **Shared Cache/Database**: If multiple replicas are required for scaling or redundancy, use a shared cache (e.g., Redis) or a central database (e.g., PostgreSQL) to ensure that a metric update to one pod in the app is visible to all pods.

By following this pattern, you centralize metric updates in a single service, keeping your application code cleaner and leveraging Prometheus’s native pull-based model.


## Step 3) Observe

After a few minutes, the observations from your custom metric should appear in your monitoring system (for example, Grafana).

## Important note on performance and storage costs

Please be aware that using too many unique labels or values (high cardinality) can quickly degrade performance and inflate storage costs in Prometheus. Labels that change frequently or include user IDs, timestamps, or other unique identifiers are particularly problematic. Always consult your system administrator or MLOps/DevOps team on best practices for label management and on setting up thresholds or limits to maintain a healthy, stable monitoring environment.

## Troubleshooting

If you do not see your metric in the monitoring system, check the following:

- **Observability Disabled?** Make sure observability is enabled for your model hosting deployment or app hosting deployment setting.
- **Verify via Pod Metrics Endpoint**: If you have the necessary Kubernetes permissions, connect to the pod running your code is hosted on and run:

  ```shell
  curl http://localhost:8000/metrics/
  ```

  You should see custom metrics like:

  ```
  # HELP my_test_counter_total My test counter
  # TYPE my_test_counter_total counter
  my_test_counter_total{my_first_dimension="abc",my_second_dimension="xyz"} 4.0
  # HELP my_test_counter_created My test counter
  # TYPE my_test_counter_created gauge
  my_test_counter_created{my_first_dimension="abc",my_second_dimension="xyz"} 1.737049965621189e+09
  ```

  - If **no metrics** appear at all, observability may not be enabled.
  - If **only your metric** is missing, ensure you are using the model version or api call that contains your custom metrics code.

- **Check Prometheus Scraping**: If the metrics are available in the pod but not in Prometheus, verify the `defaultServiceMonitor` settings in your Kubernetes namespace. This determines whether Prometheus is correctly scraping the metrics from your deployment.


---

**Previous**: [Share Workers](share-workers.md) | **Next**: [Use Graph Databases](use-graph-databases.md)
