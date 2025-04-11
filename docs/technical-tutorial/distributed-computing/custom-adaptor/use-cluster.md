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

<!-- #region -->
# Using the interactive Spark Cluster Client

- This example demonstrates how to connect to the Practicus AI Spark cluster we created, and execute simple Spark operations.
- Please run this example on the `Spark Coordinator (master)`.

## Custom Cluster Setup

Since you are working with a custom cluster, the usual method (`spark = prt.distributed.get_client()`) does not automatically create a Spark session. You have two options:

### Option 1: Manually Create a Spark Session (relatively harder)

In this option, you manually create a Spark session by specifying the master URL, port, and any additional configurations.

```python
master_addr = f"prt-svc-wn-{coordinator_instance_id}"
master_port = coordinator_port
spark_master_url = f"spark://{master_addr}:{master_port}"
conf = ...  # other configuration settings
spark = SparkSession.builder \
    .appName("my-spark-app") \
    .master(spark_master_url) \
    .config(conf=conf) \
    .getOrCreate()
```

### Option 2: Patch the Job Type Back to Spark (relatively easier)

When starting the cluster, set the distributed `job_type` to `custom`. Once the Spark cluster is running, you can switch the `job_type` back to `spark`.

To do this:
1. Load the distributed configuration (which is base64 encoded) from the OS environment.
2. Update the configuration.
3. Write the updated configuration back.

> **Note:** The change in the OS environment is temporary and will only persist for the current notebook kernel.
<!-- #endregion -->

```python
import os
import base64
import json

distributed_conf_dict_b64 = os.getenv("PRT_DISTRIBUTED_CONF", None)
distributed_conf_str = base64.b64decode(distributed_conf_dict_b64.encode("utf-8")).decode("utf-8")
distributed_conf = json.loads(distributed_conf_str)

print("Current distributed job configuration:")
print(distributed_conf)

# Let's patch job_type
distributed_conf["job_type"] = "spark"

print("Patched distributed job configuration:")
print(distributed_conf)

distributed_conf_str = json.dumps(distributed_conf)
distributed_conf_dict_b64 = base64.b64encode(distributed_conf_str.encode("utf-8")).decode("utf-8")

# And save it back to OS environment temporarily
os.environ["PRT_DISTRIBUTED_CONF"] = distributed_conf_dict_b64
```

```python
import practicuscore as prt

# Our Spark session code will work as usual
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


## Supplementary Files

### my_adaptor.py
```python
import practicuscore as prt
from practicuscore.dist_job import SparkAdaptor


class MySparkAdaptor(SparkAdaptor):
    @property
    def _run_cluster_coordinator_command(self) -> str:
        old_command = super()._run_cluster_coordinator_command

        # Change the command as needed
        new_command = old_command + " # add your changes here"

        return new_command

    @property
    def _run_cluster_agent_command(self) -> str:
        old_command = super()._run_cluster_agent_command

        new_command = old_command + " # add your changes here"

        return new_command

```


---

**Previous**: [Start Cluster](start-cluster.md) | **Next**: [Unified DevOps > Introduction](../../unified-devops/introduction.md)
