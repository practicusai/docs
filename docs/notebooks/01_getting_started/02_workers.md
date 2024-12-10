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

<!-- #region -->
# Using Workers

This example illustrates the basic workflow of creating a worker, accessing it through JupyterLab, performing tasks, and then terminating the environment when finished.

## Steps

1. **Create a Worker**:  
   From the Practicus AI interface, request a new worker with the required specifications (e.g., CPU, RAM, GPU). This process typically takes a few seconds.

2. **Access JupyterLab or VS Code**:  
   Once the worker is ready, start a JupyterLab session directly on it. Here you can:
   - Develop and run code
   - Explore and process data
   - Train and evaluate models

3. **Perform Tasks**:  
   Within the JupyterLab environment, you can execute standard Python notebooks, run scripts, or use a variety of integrated tools and libraries.

4. **Terminate the Worker**:  
   After completing your work, simply stop or delete the worker. A new worker can be created at any time, providing a clean environment without leftover state.

This workflow ensures you have an isolated, on-demand environment for efficient development and testing, while preserving the flexibility to scale resources and maintain a clean slate for subsequent tasks.


### Worker with default settings

Let's create a worker with default settings.
<!-- #endregion -->

```python
# Import the Practicus AI SDK
import practicuscore as prt
```

```python
# Select a region (assuming a single-region setup)
region = prt.get_default_region()


worker = region.create_worker()
```

```python
# Start JupyterLab on the worker and open it in a new tab
worker.open_notebook()

# To use VS Code instead of JupyterLab, uncomment the line below:
# worker.open_vscode()
```

```python
# After using the worker, you can terminate it:
worker.terminate()

# Alternatively, if you're inside the worker environment, you can 'self-terminate' by running:
# prt.get_local_worker().terminate()
```

### Customized Worker

Now let's create a worker with additional settings.

```python
# First step is to define what we need
worker_config = prt.WorkerConfig(
    # The below image has GenAI related features
    worker_image="practicus-genai",
    # Worker sizes are defined by your admin, more on this later.
    worker_size="X-Small",
    
    startup_script="""
    echo "Hello Practicus AI" > ~/hello.txt
    """,
)

# And create the worker with the custom configuration
second_worker = prt.create_worker(worker_config)
```

```python
# Verify you have hello.txt in home directory
second_worker.open_notebook()
```

```python
second_worker.terminate()
```


---

**Previous**: [Introduction](01_introduction.md) | **Next**: [Modeling Basics](../02_modeling/01_basics/modeling_basics.md)
