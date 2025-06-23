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


#### Define Parameters

```python
worker_image = "practicus-genai"
worker_size = "X-Small"
startup_script = """
echo "Hello Practicus AI" > ~/hello.txt
"""
```

```python
assert worker_image, "Please select a worker_image."
assert worker_size, "Please select a worker_size."
```

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
    worker_image=worker_image,
    worker_size=worker_size,
    startup_script=startup_script,
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

<!-- #region -->
### Advanced Worker Lifecycle Control

In advanced scenarios, you might need more granular control over a worker's startup and readiness. This is particularly useful for:

* **Extended Wait Times:** Allowing more time for workers to become ready, especially when using large container images (e.g., GPU-enabled images) that can take a significant time to download and initialize, especially on their first use on a node.
* **Proactive Termination:** Automatically terminating a worker if it fails to become ready within a specified timeframe, which can occur due to issues like resource capacity constraints or prolonged provisioning.

To enable this custom lifecycle management, you can disable the default readiness check behavior. This is achieved by setting the `wait_until_ready=False` parameter in the `prt.create_worker()` function call. You can then implement your own logic to define how long to wait for the worker and what action to take if it doesn't become ready within your defined timeout.

**Important Note:** Practicus AI will **not** automatically terminate the worker if it's readiness time-outs. This design choice allows administrators to investigate and troubleshoot the underlying cause of the worker failing to become ready. Therefore, your custom logic should explicitly include steps to terminate the worker if that is the desired outcome after a timeout.

**Sample Code:**

```python
import practicuscore as prt

# Requesting a fairly large Worker size.
# Let's assume we will not have such capacity available..
worker_size = "2X-Large"

worker_config = prt.WorkerConfig(
    worker_size=worker_size,
)

# Create the worker instance, disabling the default readiness check
# This allows for custom handling of the worker's ready state.
worker = prt.create_worker(
    worker_config=worker_config,
    wait_until_ready=False,  # Turn off the default blocking readiness check
)

# Define a custom timeout period in seconds for the worker to become ready
timeout_seconds = 120  # Example: 2 minutes, default is a minute.

try:
    print(f"Waiting up to {timeout_seconds} seconds for worker '{worker.name}' to be ready...")
    worker.wait_until_ready(timeout=timeout_seconds)
    print(f"Worker '{worker.name}' is now ready!")
    # Worker is ready, proceed with your tasks..
except TimeoutError:
    # This block executes if the worker does not become ready within the timeout period.
    # For Kubernetes admins: you will see the Worker pod is stuck in `pending` state due to capacity issues.
    print(f"Error: Worker '{worker.name}' did not become ready within {timeout_seconds} seconds.")
    print(f"Terminating worker '{worker.name}' due to readiness timeout.")
    # For Kubernetes admins: the below will remove the Worker pod, preventing auto-provisioning 
    #   if capacity becomes available later..
    worker.terminate()
except Exception as e:
    # Catch any other potential exceptions during the process
    print(f"An unexpected error occurred: {e}")
    print(f"Consider terminating worker '{worker.name}' manually if it's still running.")
    worker.terminate()  # Optionally terminate on other errors as well
```

#### Cleaning Up Workers Stuck in the `Provisioning` State

Occasionally, a Worker may remain in the `Provisioning` state longer than expected. You can identify and terminate such Workers in batch using the code below:

```python
import practicuscore as prt
from datetime import datetime, timezone

timeout_seconds = 120  # Threshold for considering a Worker as stuck

region = prt.current_region()

# Iterate through all Workers in the region
for worker in region.worker_list:
    time_since_creation = int((datetime.now(timezone.utc) - worker.creation_time).total_seconds())
    print(f"{worker.name} started {time_since_creation} seconds ago and is currently in '{worker.status}' state.")

    if worker.status == "Provisioning" and time_since_creation > timeout_seconds:
        print(f"-> Terminating {worker.name} — stuck in 'Provisioning' for more than {timeout_seconds} seconds.")
        worker.terminate()
```
<!-- #endregion -->


---

**Previous**: [Introduction](introduction.md) | **Next**: [Workspaces](workspaces.md)
