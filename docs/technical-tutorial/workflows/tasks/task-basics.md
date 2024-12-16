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

# Running Tasks on Practicus AI Workers

Before exploring orchestrations like Airflow, it’s important to grasp the fundamentals of **tasks** in Practicus AI and how they run on workers.

Practicus AI executes tasks by creating isolated, on-demand Kubernetes pods (Workers). Each task runs in its own Worker environment, ensuring scalability, isolation, and resource-efficiency.



## What is a Task?

A **task** is a unit of work, typically a Python script or shell script, that you want to execute in a controlled environment. Tasks can be composed into larger workflows or run as standalone jobs. They form the building blocks for repeatable, automated processes.


## How Practicus AI Executes Tasks

1. **Task Submission**: You define the code (e.g., a Python file `task_1.py`) along with any parameters.
2. **Worker Creation**: Practicus AI provisions a dedicated Worker pod to run your task.
3. **Task Execution**: The Worker runs your code, capturing stdout and stderr logs by default.
4. **Termination**: After completion, the Worker is automatically terminated to free up resources.

This pattern ensures that every task runs in a fresh environment and that resources are only consumed for as long as they are needed.


## Running a Task Using the Practicus AI SDK

Using the Practicus AI SDK, you can easily submit tasks to be executed on Workers. The SDK handles provisioning, running, and cleaning up the Worker, so you can focus on your code.

```python
import practicuscore as prt

# This call:
#  - Creates a new Worker
#  - Uploads files from the current directory by default
#  - Runs 'task_1.py'
#  - Captures and prints the script output
#  - Terminates the Worker after completion
prt.run_task(file_name="task_1.py")

print("Task completed and worker is terminated.")
```

```python
# Running a shell script task
prt.run_task(file_name="task_2.sh")
print("Shell task completed and worker is terminated.")
```

```python
# Customizing the worker environment

# Example startup script (uncomment to use):
# startup_script = """
# sudo apt-get update
# sudo apt-get install -y some-package
# pip install some-library
# """

worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="X-Small",
    # startup_script=startup_script,
)

# This task intentionally fails to demonstrate debugging
worker, success = prt.run_task(
    file_name="task_with_error.py",
    worker_config=worker_config,
    terminate_on_completion=False,  # Keep the worker alive to inspect
)

print("Task execution finished, next cell to investigate...")
```

```python
# If the task failed, inspect the environment.
# Uploaded files and logs are in ~/practicus/task/

if not success:
    # Opens Jupyter notebook in a new browser tab to troubleshoot
    worker.open_notebook()
```

```python
print(f"Done analyzing, now terminating {worker.name}.")
worker.terminate()
```

<!-- #region -->
## Tasks with Jupyter Notebooks

You can also run tasks defined as Jupyter notebooks:
- Dynamically pass parameters to notebooks.
- Collect and manage output artifacts.

Create `task_with_notebook.ipynb` with the below code that raises an error.

```python
print("This task runs inside a notebook.")

raise SystemError("Simulated error")
```

Create `task_with_notebook.py` that triggers the notebook we just created.

```python
import practicuscore as prt

prt.notebooks.execute_notebook(
    "task_with_notebook",
    raise_on_failure=True,
)
```

To run the notebook as a task:
<!-- #endregion -->

```python
print("Running a notebook as task")
worker, success = prt.run_task(
    file_name="task_with_notebook.py",
    terminate_on_completion=False,
)
print("Task was successful." if success else "Task failed.")
```

```python
print(f"Opening Jupyter notebook on {worker.name}.")
print("Check ~/practicus/task/ for output notebooks, e.g. task_with_notebook_output.ipynb")
worker.open_notebook()
```

```python
print("Terminating worker.")
worker.terminate()
```

## Additional Tips

- **Already logging task output?**
  - Disable additional capture using `prt.run_task(..., capture_task_output=False)`.

- **Need a custom virtual environment?**
  - Create or specify a Python venv under `~/.venv/` and run tasks with `python_venv_name="your_venv"`.

- **Running automated notebooks from CLI?**
  - Use `prtcli` commands and `.sh` scripts to trigger notebook executions.

These options give you flexibility in how tasks run, interact with environments, and handle their outputs.


## Supplementary Files

### task_1.py
```python
print("Hello from simple task 1")
```

### task_2.sh
```bash
echo "Hello from simple task 2"
```

### task_with_error.py
```python
import practicuscore as prt


def main():
    print("Starting task..")

    # Code as usual:
    # - Process data
    # - Train models
    # - Make predictions
    # - Orchestrate other tasks
    # - ...

    try:
        raise NotImplementedError("Still baking..")
    except Exception as ex:
        # Psudo detail log
        with open("my_log.txt", "wt") as f:
            f.write(str(ex))
        raise ex
    
    print("Finished task..")


if __name__ == '__main__':
    main()
```


---

**Previous**: [Introduction](../introduction.md) | **Next**: [Deploying On Airflow](../airflow/deploying-on-airflow.md)
