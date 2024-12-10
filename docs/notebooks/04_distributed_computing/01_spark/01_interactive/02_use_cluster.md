---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Using the interactive Spark Cluster Client

- This notebook demonstrates how to connect to the Practicus AI Spark cluster we created, and execute simple Spark operations.
- Please run this notebook on the `Spark Coordinator (master)`.

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

<!-- #endregion -->

```python

```


---

**Previous**: [Start Cluster](01_start_cluster.md) | **Next**: [Batch Job](../02_batch_job/batch_job.md)