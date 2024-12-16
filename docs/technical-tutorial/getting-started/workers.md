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

# Practicus AI Workers

This example demonstrates a typical workflow for using Practicus AI Workers:

**Create a Worker**:  

Request a new worker with the required resources (CPU, RAM, GPU) from Practicus AI. This usually takes a few seconds.

**Open JupyterLab or VS Code**:

Once the worker is ready, launch JupyterLab or VS Code directly on it. Within this environment, you can:

- Develop and run code interactively
- Explore and process data
- Train and evaluate machine learning models

**Perform Tasks**:  

Inside JupyterLab or VS Code, run Python notebooks, scripts, or leverage integrated libraries and frameworks.

**Terminate the Worker**:  

After finishing your tasks, stop or delete the worker. You can always start a new one later, ensuring a clean environment each time.

This approach provides an isolated, on-demand environment for efficient development, scaling, and maintaining a clean slate for each new task.

### Creating a Worker with Default Settings

Let's start by creating a worker with the default configuration.

```python
# Import the Practicus AI SDK
import practicuscore as prt
```

```python
# Create a worker using default settings
worker = prt.create_worker()
```

```python
# Start JupyterLab on the worker and open it in a new browser tab
worker.open_notebook()

# To use VS Code instead of JupyterLab, uncomment the line below:
# worker.open_vscode()
```

```python
# After using the worker, terminate it:
worker.terminate()

# If you're inside a worker environment, you can self-terminate by running:
# prt.get_local_worker().terminate()
```

### Creating a Customized Worker

Now let's create a worker with a custom configuration, specifying a custom image, size, and a startup script.

```python
# Define a custom worker configuration
worker_config = prt.WorkerConfig(
    worker_image="practicus-genai",
    worker_size="X-Small",
    startup_script="""
    echo "Hello Practicus AI" > ~/hello.txt
    """,
)

# Create the worker with the custom configuration
worker = prt.create_worker(worker_config)
```

```python
# Verify that hello.txt exists in the home directory:
worker.open_notebook()
```

```python
worker.terminate()
```

### Working with the Region Class

- You can interact with multiple regions and perform most operations by using the [Region](https://docs.practicus.ai/sdk/practicuscore.html#Region) class.
- If running inside a worker, you can easily access the current region and perform actions directly.

```python
# Get the current region
region = prt.current_region()

# You could also connect to a different region
# region = prt.get_region("username@some-other-region.com")
```

```python
print("Current region:")
region
```

It will print something like:

```
key: my-user-name@practicus.your-company.com
url: https://practicus.your-company.com
username: my-user-name
email: my-user-name@your-company.com
is_default: True
```


### Worker Sizes

Worker sizes define the CPU, RAM, GPU, and other resources allocated to a worker.

```python
# List available worker sizes
for worker_size in region.worker_size_list:
    print(worker_size.name)
```

### Smart Listing with PrtList

[PrtList](https://docs.practicus.ai/sdk/practicuscore.html#PrtList) is a specialized list type that can be toggled as read-only and easily converted to CSV, DataFrame, or JSON. Many results returned by the SDK are `PrtList` objects.

```python
# Convert worker sizes to a pandas DataFrame
df = region.worker_size_list.to_pandas()
display(df)
```

### Worker Images

Worker images define the base container image and features available on the worker.

```python
df = region.worker_image_list.to_pandas()
print("Available worker images:")
display(df)
```

### Worker Logs

You can view the logs of a worker to debug issues or review activities.

```python
if prt.running_on_a_worker():
    print("Code is running on a worker, will use 'self' (local worker).")
    worker = prt.get_local_worker()
else:
    print("Code not running on a worker, creating a new one.")
    worker = prt.create_worker()

print("Worker logs:")
worker.view_logs()

worker_logs = worker.get_logs()
if "some error" in worker_logs:
    print("Found 'some error' in logs")
```


---

**Previous**: [Introduction](introduction.md) | **Next**: [Workspaces](workspaces.md)
