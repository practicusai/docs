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

# Executing batch jobs in Dask Cluster

In this example we will:
- Create a Dask cluster
- Submit a job python file
- Terminate the cluster after job is completed.

### Before you begin
- Create "dask" under your "~/my" folder
- And copy job.py under this folder

```python
worker_size = None
worker_count = None
log_level = "DEBUG"
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert log_level, "Please enter your log_level."
```

```python
import practicuscore as prt

job_dir = "~/my/dask"

distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.dask,
    job_dir=job_dir,
    py_file="job.py",
    worker_count=worker_count,
)

worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    distributed_config=distributed_config,
    log_level=log_level,
)

coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
```

```python
prt.distributed.live_view(
    job_dir=job_dir,
    job_id=coordinator_worker.job_id,
)
```

```python
# You can view the logs during or after the job is completed
# To view coordinator (master) set rank = 0
rank = 0
# To view other workers set rank = 1,2, ..

prt.distributed.view_log(job_dir=job_dir, job_id=coordinator_worker.job_id, rank=rank)
```

### Wrapping up
- Once the job is completed, you can view the results in `~/my/dask/result.csv/`
- Please note that result.csv is a folder that can contain `parts of the processed file` by each worker (Dask executors)
- Also note that you do **not** need to terminate the cluster since it has a 'py_file' to execute, which defaults `terminate_on_completion` parameter to True.
- You can change terminate_on_completion to False to keep the cluster running after the job is completed to troubleshoot issues.
- You can view other `prt.DistJobConfig` properties to customize the cluster


## Supplementary Files

### job.py
```python
import practicuscore as prt
import dask.dataframe as dd

# Let's get a Dask session
print("Getting Dask session")
dask = prt.distributed.get_client()

print("Reading diamond data")
df = dd.read_csv("/home/ubuntu/samples/data/diamond.csv")

print("Calculating")
df["New Price"] = df["Price"] * 0.8

print("Since Dask is a lazy execution engine,")
print(" actual calculations will happen when you call compute() or save.")

print("Saving")
df.to_csv("/home/ubuntu/my/dask/result.csv")

# Note: the save location must be accessible by all workers
# A good place to save for distributed processing is object storage

```


---

**Previous**: [Use Cluster](../interactive/use-cluster.md) | **Next**: [Distributed Training > XGBoost](../distributed-training/xgboost.md)
