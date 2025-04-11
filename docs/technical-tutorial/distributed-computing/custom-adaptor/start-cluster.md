---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Customizing Distributed Clusters with Custom Adaptors

This example demonstrates how to customize Practicus AI distributed cluster or job engine by creating a subclass of one of the existing classes and overriding its methods and properties as needed.

#### Note on shared drives

- Practicus AI distributed clusters require a shared drive accessible by multiple workers, such as Practicus AI `~/my` or `~/shared` folders.
- If you do not have access to ~/my or ~/shared folders, please check the auto-scaled examples which does not need such drives, but are limited in functionality.

```python
worker_size = None
worker_count = None
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
```

### Copy the contents of this folder to ~/my/custom_adaptor

```python
import os

assert os.path.exists("/home/ubuntu/my/custom_adaptor/my_adaptor.py"), (
    "Please copy the contents of this folder to ~/my/custom_adaptor"
)
```

```python
# Understanding methods and properties to override
# Let's customize SparkAdaptor
from practicuscore.dist_job import SparkAdaptor

print("SparkAdaptor methods and properties:")
print(dir(SparkAdaptor))

# Please view my_adaptor.py for an example overriding coordinator and agent startup command.
```

```python
import practicuscore as prt

# Let's define the distributed features
distributed_config = prt.DistJobConfig(
    worker_count=worker_count,
    # Let's change job_type to custom
    job_type=prt.DistJobType.custom,
    # Job directory must have the .py file of our custom adaptor
    job_dir="/home/ubuntu/my/custom_adaptor",
    # MySparkAdaptor class in my_adaptor.py
    custom_adaptor="my_adaptor.MySparkAdaptor",
)

# Let's define worker features of the cluster
worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    distributed_config=distributed_config,
    # Turn on debug logging so we can troubleshoot custom adaptor issues.
    log_level="DEBUG",
)

# Creating the coordinator (master) worker
# will also create the cluster.
coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
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

**Previous**: [Use Cluster](../ray/vllm/use-cluster.md) | **Next**: [Use Cluster](use-cluster.md)
