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

# Starting an auto-scaled Spark Cluster

- This notebook demonstrates how to create, and connect to a Practicus AI Spark auto-scaled cluster, and execute simple Spark operations. 

### Important note on privileged access

- For auto-scaled Spark to work, `you will need additional privileges` on the Kubernetes cluster.
- Please ask your admin to grant you access to worker size definitions with privileged access before you continue with this notebook.

### Important note on worker container image

- Unlike standard Spark cluster, auto-scaled Spark cluster executors have a separate type of container image ghcr.io/practicusai/practicus-spark
- This means packages acceesible to coordinator worker might not be accessible to the executors.
- To install packages please install to both the coordinator and the executor images and create custom container images.
- While creating the spark client, you can then pass arguments to specify which executor image to use.

```python
import practicuscore as prt

# Let's define the distributed features
distributed_config = prt.distributed.JobConfig(
    job_type = prt.distributed.JobType.spark,
    # ** The below changes the default cluster behavior **
    auto_distributed=True,
    # Set the initial size. 
    # These are 'additional` executors to coordinator, 
    # E.g. the below will create a cluster of 2 workers.
    initial_count=1,
    # Optional: set a maximum to auto-scale to, if needed.
    # E.g. with the below, the cluster can scale up to 5 workers
    max_count=4,
)

# Let's define worker features of the cluster 
worker_config = prt.WorkerConfig(
    # ** Set a worker size config with privileged access **
    worker_size="X-Small-Privileged",
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
