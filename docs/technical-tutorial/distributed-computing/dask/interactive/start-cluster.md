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

# Starting an interactive Dask Cluster

- This example demonstrates how to create, and connect to a Practicus AI Dask cluster, and execute simple Dask operations.

#### Note on shared drives

- Practicus AI distributed clusters require a shared drive accessible by multiple workers, such as Practicus AI `~/my` or `~/shared` folders.
- If you do not have access to ~/my or ~/shared folders, please check the auto-scaled examples which does not need such drives, but are limited in functionality.

```python
import practicuscore as prt

# Let's define the distributed features
distributed_config = prt.distributed.JobConfig(
    job_type = prt.distributed.JobType.dask,
    worker_count = 2,
)

# Let's define worker features of the cluster 
worker_config = prt.WorkerConfig(
    worker_size="X-Small",
    distributed_config=distributed_config,
)

# Creating the coordinator (master) worker 
# will also create the cluster.
coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
```

```python
# Since this is an interactive Dask cluster,
#  let's login to execute some code.

notebook_url = coordinator_worker.open_notebook()

print("Page did not open? You can open this url manually:", notebook_url)
```

### Please continue experimenting on the new browser tab

by opening the next example in this directory

```python
# Done experimenting? Let's terminate the coordinator 
#  which will also terminate the cluster.
coordinator_worker.terminate()
```

```python

```


---

**Previous**: [Batch Job](../../spark/auto-scaled/batch/batch-job.md) | **Next**: [Use Cluster](use-cluster.md)
