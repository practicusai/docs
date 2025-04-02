---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Using the interactive Spark Cluster Client

- This example demonstrates how to connect to the Practicus AI Spark cluster we created, and execute simple Spark operations.
- Please run this example on the `Spark Coordinator (master)`.

```python
import practicuscore as prt 

# Let's get a Spark session
spark = prt.distributed.get_client()
```

```python
# And execute some code
data = [("Alice", 29), ("Bob", 34), ("Cathy", 23)]
columns = ["Name", "Age"]

# Create a DataFrame
df = spark.createDataFrame(data, columns)

# Perform a transformation
df_filtered = df.filter(df.Age > 30)

# Show results
df_filtered.show()
```

```python
# Let's end the session
spark.stop()
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

### Troubleshooting

If you’re experiencing issues with an interactive cluster that doesn’t run job/train.py, please follow these steps:

1. **Agent Count Mismatch**:
   If the number of distributed agents shown by `prt.distributed.get_client()` is less than what you expected, wait a moment and then run `get_client()` again. This is usually because the agents have not yet joined the cluster.
   *Note: Batch jobs automatically wait for agents to join.*

2. **Viewing Logs**:
   To view logs, navigate to the `~/my/.distributed` folder.

<!-- #endregion -->


---

**Previous**: [Start Cluster](start-cluster.md) | **Next**: [Batch Job > Batch Job](../batch-job/batch-job.md)
