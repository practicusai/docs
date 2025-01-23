---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Using the interactive Ray Cluster for Modin

- This example demonstrates how to connect to the Practicus AI Ray cluster we created, and execute modin + Ray operations.
- Please run this example on the `Ray Coordinator (master)`.

```python
import practicuscore as prt 

# Let's get a Ray session.
# this is similar to running `import ray` and then `ray.init()`
ray = prt.distributed.get_client()
```

```python
# Modin aims to be a drop-in replacement for pandas
# import pandas as pd
import modin.pandas as pd

df = pd.read_csv("/home/ubuntu/samples/airline.csv")

print("DataFrame type is:", type(df))

df["passengers"] = df["passengers"] * 2

df
```

### Ray Dashboard

Practicus AI Ray offers an interactive dashboard where you can view execution details. Let's open the dashboard.

```python
dashboard_url = prt.distributed.open_dashboard()

print("Page did not open? You can open this url manually:", dashboard_url)
```

```python
df["passengers"] = df["passengers"] * 2

df
```

```python
# Let's close the session
ray.shutdown()
```

<!-- #region -->
### Terminating the cluster

- You can go back to the other worker where you created the cluster to run:

```python
coordinator_worker.terminate()
```
- Or, terminate "self" and children workers with the below:

```python
prt.get_local_worker().terminate()
```

<!-- #endregion -->


---

**Previous**: [Start Cluster](start-cluster.md) | **Next**: [Vllm > Start Cluster](../vllm/start-cluster.md)
