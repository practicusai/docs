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

# Distributed vLLM with Ray

- This example demonstrates how to create, and connect to a Practicus AI Ray cluster, and execute simple vLLM + Ray operations.
- Although the example is interactive, you can apply the same for batch jobs as well.

#### Note on shared drives

- Practicus AI distributed clusters require a shared drive accessible by multiple workers, such as Practicus AI `~/my` or `~/shared` folders.
- If you do not have access to ~/my or ~/shared folders, please check the auto-scaled examples which does not need such drives, but are limited in functionality.

```python
worker_size = "X-Small"
worker_count = 2
worker_image = "practicus-gpu-vllm"
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert worker_image, "Please enter your worker_image."
```

```python
import practicuscore as prt

# Let's define the distributed features
distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.ray,
    worker_count=worker_count,
)

# Let's define worker features of the cluster
worker_config = prt.WorkerConfig(
    # Please note that this example requires GPUs
    # Please note that Ray requires a specific worker image
    worker_image=worker_image,
    worker_size=worker_size,
    distributed_config=distributed_config,
)

# Creating the coordinator (master) worker
# will also create the cluster.
coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
```

```python
# Since this is an interactive Ray cluster,
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


---

**Previous**: [Use Cluster](../modin/use-cluster.md) | **Next**: [Use Cluster](use-cluster.md)
