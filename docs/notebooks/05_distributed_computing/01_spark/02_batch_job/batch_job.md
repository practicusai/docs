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

# Executing batch jobs in Spark Cluster

In this notebook we will:
- Create a Spark cluster
- Submit a job python file
- Terminate the cluster after job is completed.

### Before you begin
- Create "spark" under your "~/my" folder
- And copy job.py under this folder

```python
import practicuscore as prt

job_dir = "~/my/spark"

distributed_config = prt.distributed.JobConfig(
    job_type = prt.distributed.JobType.spark,
    job_dir = job_dir,
    py_file = "job.py",
    worker_count = 2,
)

worker_config = prt.WorkerConfig(
    worker_size="X-Small",
    distributed_config=distributed_config,
    log_level="DEBUG",
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

### Wrapping up
- Once the job is completed, you can view the resuls in `~/my/spark/result.csv/`
- Please note that result.csv is a folder that contains `parts of the processed file` by each worker (Spark executors)
- Also note that you do not need to terminate the cluster since it has a 'py_file' to execute, which defaults `terminate_on_completion` parameter to True.
- You can change terminate_on_completion to False to keep the cluster running after the job is completed to troubleshoot issues.
- You can view other `prt.distributed.JobConfig` properties to customize the cluster

```python

```


## Supplementary Files

### job.py
```python
import practicuscore as prt 

# Let's get a Spark session
print("Getting Spark session")
spark = prt.distributed.get_client()

data = [("Alice", 29), ("Bob", 34), ("Cathy", 23)]
columns = ["Name", "Age"]

print("Creating DataFrame")
df = spark.createDataFrame(data, columns)

print("Calculating")
df_filtered = df.filter(df.Age > 30)

print("Writing to csv")
df_filtered.write.csv("/home/ubuntu/my/spark/result.csv", header=True, mode="overwrite")

```


---

**Previous**: [Use Cluster](../01_interactive/02_use_cluster.md) | **Next**: [Start Cluster](../03_auto_scaled/01_start_cluster.md)
