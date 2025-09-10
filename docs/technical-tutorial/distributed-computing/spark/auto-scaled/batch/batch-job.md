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

<!-- #region -->
# Starting a Batch Job on auto-scaled Spark Cluster

This example demonstrates how to set up and run an auto-scaled batch job in Practicus AI. Instead of launching a fixed-size environment, we will create a batch job with the ability to automatically scale its compute resources based on demand.


### Important note on worker container image

- Unlike standard Spark cluster, auto-scaled Spark cluster executors have a separate type of container image `ghcr.io/practicusai/practicus-spark`
- This means packages accessible to coordinator worker might not be accessible to the executors.
- To install packages please install to both the coordinator and the executor images and create custom container images.
- While creating the spark client, you can then pass arguments to specify which executor image to use.

### Important note on privileged access

- For auto-scaled Spark to work, `you will need additional privileges` on the Kubernetes cluster.
- Please ask your admin to grant you access to worker size definitions with privileged access before you continue with this example.

### Finding an Auto-Scaled (Privileged) Worker Size

Let's identify a worker size that supports auto-scaling and includes the required privileged capabilities for running batch jobs.
<!-- #endregion -->

```python
import practicuscore as prt

region = prt.get_default_region()
```

```python
auto_dist_worker_size = None
```

If you don't know your auto-distributed (privileged) workers you can check them out by using the SDK like down below:

```python
worker_size_list = region.worker_size_list
display(worker_size_list.to_pandas())  # Check auto_distributed col.
```

```python
assert auto_dist_worker_size, "Please select an auto-distributed (privileged) worker sizes."
```

```python
# Configure distributed job settings
# This example uses Spark with auto-scaling capabilities.
distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.spark,
    auto_distributed=True,  # Enables automatic scaling of the Spark cluster
    initial_count=1,  # Start with 1 executor plus the coordinator (2 workers total)
    max_count=4,  # Allow the cluster to scale up to 4 additional executors if needed
)

# Define the worker configuration
# Ensure that the chosen worker size includes privileged access
# to support auto-scaling.
worker_config = prt.WorkerConfig(
    worker_size=auto_dist_worker_size,
    distributed_config=distributed_config,
)

# Note: We are not creating a coordinator worker interactively here
# since this setup is intended for batch tasks rather than interactive sessions.
# Example: coordinator_worker = prt.create_worker(worker_config)
```

```python
# Running the batch job:
# - Starts a worker
# - Submits 'job.py' to run on the cluster
# - 'job.py' creates a Spark session and triggers cluster creation
#   with multiple executors as defined above.
# - Monitors execution and prints progress
# - On completion, terminates the Spark session and executors
worker, success = prt.run_task(
    file_name="job.py",
    worker_config=worker_config,
    terminate_on_completion=False,  # Leave the cluster running until we decide to terminate
)
```

```python
if success:
    print("Job is successful, terminating cluster.")
    worker.terminate()
else:
    print("Job failed, opening notebook on coordinator to analyze.")
    worker.open_notebook()
```


## Supplementary Files

### job.py
```python
import practicuscore as prt

print("Requesting a Spark session...")
spark = prt.distributed.get_client()

# Create a sample DataFrame
data = [("Alice", 29), ("Bob", 34), ("Cathy", 23)]
columns = ["Name", "Age"]
print("Creating DataFrame...")
df = spark.createDataFrame(data, columns)

print("Applying filter: Age > 30")
df_filtered = df.filter(df.Age > 30)

print("Filtered results:")
df_filtered.show()

# Note:
# Auto-scaled Spark executors are different from standard Practicus AI workers.
# They use a specialized container image and do not have direct access to
# `~/my` or `~/shared` directories.
# For saving results, consider using a data lake or object storage.

```


---

**Previous**: [Use Cluster](../interactive/use-cluster.md) | **Next**: [Dask > Interactive > Start Cluster](../../../dask/interactive/start-cluster.md)
