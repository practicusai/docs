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

# Executing batch jobs in Spark Cluster

In this example we will:

- Create a Spark cluster
- Submit a job python file
- Terminate the cluster after job is completed.

### Before you begin

- Create "spark" under your "~/my" folder
- And copy job.py under this folder


```python
worker_size = None
worker_count = None
log_level = "DEBUG"
create_spark_folder = False

```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert log_level, "Please enter your log_level."
assert create_spark_folder, "Please enter your create_spark_folder"
```

```python
import os
import shutil

if create_spark_folder:
    # Define source and destination
    source_dir = "samples/notebooks/05_distributed_computing/02_spark/02_batch_job"
    source_file = f"{source_dir}/job.py"

    # Move it to '~/my', which is your persistent home directory.
    job_dir = os.path.expanduser("~/my/spark")
    dest_file = f"{job_dir}/job.py"

    # Copy the job file to the shared location
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)

    print(f"Copying job file from '{source_file}' to '{dest_file}'...")
    try:
        shutil.copy(source_file, dest_file)
        print("✅ Copy successful.")
    except FileNotFoundError:
        print(f"❌ Error: Could not find source file at {source_file}")
else:
    job_dir = "~/my/spark"
```

```python
import practicuscore as prt

# Configure the job to run from the SHARED location
distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.spark,
    job_dir=job_dir,  # <--- Point to the shared directory
    py_file="job.py",
    worker_count=worker_count,
)

worker_config = prt.WorkerConfig(
    worker_image="ghcr.io/practicusai/practicus-spark-worker",  # Or just "practicus-spark"
    worker_size=worker_size,
    distributed_config=distributed_config,
    log_level=log_level,
)

print("Submitting Spark Batch Job...")
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

- Once the job is completed, you can view the results in `~/my/spark/result.csv/`
- Please note that result.csv is a folder that contains `parts of the processed file` by each worker (Spark executors)
- Also note that you do not need to terminate the cluster since it has a 'py_file' to execute, which defaults `terminate_on_completion` parameter to True.
- You can change terminate_on_completion to False to keep the cluster running after the job is completed to troubleshoot issues.
- You can view other `prt.DistJobConfig` properties to customize the cluster



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

**Previous**: [Use Cluster](../interactive/use-cluster.md) | **Next**: [Auto Scaled > Interactive > Start Cluster](../auto-scaled/interactive/start-cluster.md)
