---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

###  Practicus AI Workers 

Practicus AI Workers live in a Practicus AI region and you can create, work with and terminate them as the below.


#### Simple use of workers

```python
import practicuscore as prt

# Workers are created under a Practicus AI region
region = prt.current_region()

# You can also connect to a remote region instead of the default one
# region = prt.get_region(..)
```

```python
# Let's view our region
region
```

```python
# The below is the easiest way to start working with a worker 
worker = region.get_or_create_worker()
```

```python
# Let's view worker details
worker
```

```python
# Let's load a sample file on the Worker
some_data_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/ice_cream.csv"
}
with worker.load(some_data_conn) as proc:
    df = proc.get_df_copy()
    # Exiting the 'with' will free up the process
```

```python
# The rest is business as usual..
df
```

#### Behind the scenes..

```python
# Let's break down what the below code actually does
# worker = region.get_or_create_worker()

if prt.running_on_a_worker():
    print("Since I am already running on a worker, let's use this one!")
    worker = prt.get_local_worker()
else:
    print("I am running on my laptop, let's get a worker.")
    print("Do I already have running workers?")
    if len(region.worker_list) > 0:
        print("Yes, I do have workers, let's use one of them.")
        worker = region.worker_list[0]
        # The real code is actually a bit smarter,
        # it will give the worker with the max memory
    else:
        print("I don't have a worker. Let's create a new one!")
        worker = prt.create_worker()

print("My worker details:")
worker
```

```python
# Always terminate the workers once you are done

if prt.running_on_a_worker():
    print("The worker is terminating itself..")
    print("Please make sure you are not losing any active workon this worker.")

worker.terminate()
```

#### Customizing workers

```python
# We can choose the size, container image and also configure other parameters
worker_config = {
    "worker_size": "X-Small",
    "worker_image": "practicus",
    # # Assign distributed worker settings
    # "distributed_conf_dict": {
    #     "max_count": 0,
    #     "initial_count": 0,
    #     "memory_mb": 1024
    # },
    # # To enforce image pull policy to Always, make the below True
    # # Only use in dev/test where you cannot easily upgrade image versions
    # "k8s_pull_new_image": False,
    # # To skip SSL verification
    # # Only use in dev/test and for self signed SSL certificates
    # "bypass_ssl_verification": False
}
worker = region.create_worker(worker_config)
```

```python
# If you do not know which worker sizes you have access to:
region.worker_size_list.to_pandas()
```

```python

```

```python
# If you do not know which worker container images you have access to:
region.worker_image_list.to_pandas()
```

```python
# Let's iterate over workers
for worker in region.worker_list:
    print("Worker details:", worker)
```

```python
# We can also realod workers.
# This is useful if you create workers from multiple systems
region.reload_worker_list()
```

```python
# Converting the worker_list into string will give you a csv 
print(region.worker_list)
```

```python
# You can also get workers as a pandas DataFrame for convenience
region.worker_list.to_pandas()
```

```python
# Simply accessing the worker_list will print a formatted table string 
region.worker_list
```

```python
first_worker = region.worker_list[0]
# Accessing an worker object will print it's details
first_worker
```

```python
worker_name = first_worker.name
print("Searching for:", worker_name)
# You can locate a worker using it's name
worker = region.get_worker(worker_name)
print("Located:", worker)
# Or using worker index only, e.g. 123 for Worker-123
# region.get_worker(123)
```

### Worker Logs

```python
# You can view worker logs like the below 
worker.view_logs()

# To get logs as a string 
worker_logs = worker.get_logs()

# E.g. to search for an error string
print("some error" in worker_logs)
```

### Cleaning up

```python
# There are multiple ways to terminate a worker.
worker.terminate()
# Or, 
# region.terminate_worker(worker_name)
# Worker number works too
# region.terminate_worker(123)
```

```python
# The below will terminate all of your workers
region.terminate_all_workers()
```


---

**Previous**: [Streamlined Model Deployment](../additional-modeling/streamlined-model-deployment/streamlined-model-deployment.md) | **Next**: [Use Workspaces](use-workspaces.md)
