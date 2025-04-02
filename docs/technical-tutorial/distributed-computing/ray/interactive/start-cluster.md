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

# Starting an interactive Ray Cluster

- This example demonstrates how to create, and connect to a Practicus AI Ray cluster, and execute simple Ray operations.

#### Note on shared drives

- Practicus AI distributed clusters require a shared drive accessible by multiple workers, such as Practicus AI `~/my` or `~/shared` folders.
- If you do not have access to ~/my or ~/shared folders, please check the auto-scaled examples which does not need such drives, but are limited in functionality.

```python
worker_size = None  
worker_count = None
worker_image = "practicus-ray"
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
    job_type = prt.DistJobType.ray,
    worker_count = worker_count,
)

# Let's define worker features of the cluster 
worker_config = prt.WorkerConfig(
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

**Previous**: [Llms With DeepSpeed](../../deepspeed/llm-fine-tuning/llms-with-deepspeed.md) | **Next**: [Use Cluster](use-cluster.md)
