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

### Running Tasks on Practicus AI Workers

Before diving into Airflow and orchestrating workflows, it's important to understand the fundamental concept of **tasks** in the Practicus AI platform and how they are executed. Practicus AI provides a streamlined system to execute user-defined code within isolated, scalable Kubernetes pods, called **Practicus AI Workers**. Here’s how it works:

---

#### What is a Task?

A **task** in Practicus AI is a unit of work that encapsulate the **code**: A Python function, bash script, or any logic defined by the user.

Tasks are designed to be executed independently, making them ideal building blocks for larger workflows.

---

#### How Practicus AI Executes Tasks

Practicus AI creates, manages, and terminates isolated worker Kubernetes pods for each task execution. This ensures:
- **Scalability**: Resources are provisioned dynamically based on the workload.
- **Isolation**: Each task runs in its own containerized environment, avoiding interference.
- **Flexibility**: Custom user code can be executed safely with controlled resources.

Here’s the lifecycle of a task:

1. **Task Submission**:
   - You define a task using the Practicus AI SDK.
   - Tasks can include parameters, dependencies, and required artifacts.

2. **Worker Creation**:
   - Practicus AI provisions the worker for the task.
   - The worker is initialized with the necessary environment, including the code, parameters, and dependencies.

3. **Task Execution**:
   - The worker pod runs the customer’s code.
   - Standard output (`stdout`) and error (`stderr`) are captured for logging, which can be disabled.

4. **Worker Pod Termination**:
   - After task execution is complete, the worker pod is automatically terminated to free up resources.
   - You can also disable worker termination to open the notebook after executing the task worker to troubleshoot issues.

---

#### Running a Task Using the Practicus AI SDK

Practicus AI provides an SDK to simplify task submission and execution. Below is an example workflow for running a task using the SDK:

```python
import practicuscore as prt
```

```python
# The below will:
# - Start a new worker with default settings
# - Upload the files located in this folder
# - Run task_1.py
# - Capture the script output and display
# - Terminate the worker

prt.run_task(file_name="task_1.py")

print("Completed the task and worker is terminated..")
```

```python
# You can also run a shell script.

prt.run_task(file_name="task_2.sh")

print("Completed the task and worker is terminated..")
```

```python
# Let's customize the worker that the task runs on

# Sample startup script, worker will not get ready before this completes running.
startup_script = """
sudo apt-get update 
sudo apt-get install -y some-package
pip install some-library
"""

worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="X-Small",
    # startup_script=startup_script,
)

# This task will fail and you can view the error message in logs
worker, success = prt.run_task(
    file_name="task_with_error.py",
    worker_config=worker_config,
    terminate_on_completion=False,  # will manually terminate
)

print("Execute next cell to further investigate..")
```

```python
# Failed? Let's troubleshoot..
# Task files are uploaded and run under ~/practicus/task/

if not success:
    # The below will open a Jupyter notebook in a new tab
    worker.open_notebook()
```

```python
print(f"Done analyzing, terminating {worker.name}")
worker.terminate()
```

#### Tasks with Jupyter notebooks

- You can use Jupyter notebooks for your tasks and other automation needs.
- Automated notebooks have many features, including:
    - Dynamic notebook parameters.
    - Routing failed notebooks to designated locations.
- To learn more, please check the samples under:
    - ~/samples/notebooks/05_others/automated_notebooks

```python
# As a first step, create "task_with_notebook.ipynb" file and add the below

print("This task is running in a notebook")

# Code as you would normally do..

import practicuscore as prt

region = prt.get_default_region()

print("Task is running with login credentials of", region.email)

print("Let's simulate a failure")

raise SystemError("Simulated error")
```

```python
# And then create "task_with_notebook.py" and add the below

import practicuscore as prt 

print("Starting to run notebook.")

prt.notebooks.execute_notebook(
    "task_with_notebook",
    # By default failed notebooks will not fail caller and just print result.
    # Since this is a task, let's fail the task too.
    raise_on_failure=True,
)

print("Notebook completed running without issues.")

```

```python
worker, success = prt.run_task(
    # The .py task file here is a trigger for the notebook
    file_name="task_with_notebook.py",
    terminate_on_completion=False,
)

print("Task was successful." if success else "Task failed.")
```

```python
print(f"Opening Jupyter notebook on {worker.name}.")
print("You can view the notebook output in ~/practicus/task/*")
print("> Look for task_with_notebook_output.ipynb")
worker.open_notebook()
```

```python
print("Terminating worker.")
worker.terminate()
```

#### Other Topics

- Already logging your task output?
    - You can disable with setting:
    - prt.run_task(.., capture_task_output=False)
- Need a custom virtual environment?
    - Installed under "~/.venv"
    - Create a new container image and set:
    - prt.run_task(.., python_venv_name="your_venv")
    - Run the task using this image
- Run automated notebooks from CLI?
    - You can also trigger a notebook with 'prtcli' command from an .sh file.

```python

```


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

**Previous**: [Modeling Basics](../../02_modeling/01_basics/modeling_basics.md) | **Next**: [Airflow](../02_airflow/airflow.md)
