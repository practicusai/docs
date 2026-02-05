---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# Starting an auto-scaled Spark Cluster

- This example demonstrates how to create, and connect to a Practicus AI Spark auto-scaled cluster, and execute simple Spark operations. 

### Important note on worker container image

- Unlike standard Spark cluster, auto-scaled Spark cluster executors have a separate type of container image ghcr.io/practicusai/practicus-spark
- This means packages accessible to coordinator worker might not be accessible to the executors.
- To install packages please install to both the coordinator and the executor images and create custom container images.
- While creating the spark client, you can then pass arguments to specify which executor image to use.

### Important note on privileged access

- For auto-scaled Spark to work, `you will need additional privileges` on the Kubernetes cluster.
- Please ask your admin to grant you access to worker size definitions with privileged access before you continue with this example.

### Finding an Auto-Scaled (Privileged) Worker Size

Let's identify a worker size that supports auto-scaling and includes the required privileged capabilities for running batch jobs.

```python
auto_dist_worker_size = None  # E.g. "Small-Cluster"
initial_count = None  # E.g. 2
max_count = None  # E.g. 4
```

```python
assert auto_dist_worker_size, "Please type your distributed worker size"
assert initial_count, "Please enter your initial count number"
assert max_count, "Please enter your max count number"
```

```python
import practicuscore as prt

region = prt.get_default_region()
```

If you don't know your auto-distributed (privileged) workers you can check them out by using the SDK like down below:

```python
worker_size_list = region.worker_size_list
display(worker_size_list.to_pandas())  # Check auto_distributed col.
```

```python
assert auto_dist_worker_size, "Please select auto-distributed (privileged) worker size."
assert initial_count, "Please select initial_count."
assert max_count, "Please select max_count."
```

```python
# Let's define the distributed features
distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.spark,
    # ** The below changes the default cluster behavior **
    auto_distributed=True,
    # Set the initial size.
    # These are 'additional` executors to coordinator,
    # E.g. the below will create a cluster of 2 workers.
    initial_count=initial_count,
    # Optional: set a maximum to auto-scale to, if needed.
    # E.g. with the below, the cluster can scale up to 5 workers
    max_count=max_count,
)

# Let's define worker features of the cluster
worker_config = prt.WorkerConfig(
    worker_image="ghcr.io/practicusai/practicus-spark-worker:25.5.4",
    # Please make sure to use a worker size with
    #   privileged access.
    worker_size=auto_dist_worker_size,
    distributed_config=distributed_config,
)

# Creating the coordinator (master) worker:
coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
# - The above will NOT create the executors instantly.
# - You will only create one worker.
# - Additional executors will be created when needed.
```

```python
# Since this is an interactive Spark cluster,
#  let's login to execute some code.

notebook_url = coordinator_worker.open_notebook()

print("Page did not open? You can open this url manually:", notebook_url)
```

### Please continue experimenting on the new browser tab
by opening the next notebook in this directory

```python
# Done experimenting? Let's terminate the coordinator
#  which will also terminate the cluster.
coordinator_worker.terminate()
```


---

**Previous**: [Batch Job](../../batch-job/batch-job.md) | **Next**: [Use Cluster](use-cluster.md)
