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

# Customizing Task Parameters

This example demonstrates how to customize and pass parameters to a Practicus AI worker. You can do so by defining environment variables in the `WorkerConfig` object.

## Why Environment Variables?
Environment variables are often the easiest way to inject small pieces of configuration or parameters into a script. Practicus AI automatically sets these environment variables in the worker's environment when your script runs.

## Basic Example
In this simple example, we show how to set environment variables in `WorkerConfig` and then access them in a Python script.

```python
# task.py
import os

print("First Param:", os.environ["MY_FIRST_PARAM"])
print("Second Param:", os.environ["MY_SECOND_PARAM"])
```

### Defining `WorkerConfig` with Environment Variables
Below, we create a `WorkerConfig` object. Notice how we specify environment variables in the `env_variables` dictionary. Practicus AI will ensure these variables are set when `task.py` is executed.

```python
import practicuscore as prt

worker_config = prt.WorkerConfig(
    worker_image="practicus",  # The base container image
    worker_size="X-Small",     # Size configuration
    env_variables={
        "MY_FIRST_PARAM": "VALUE1",
        "MY_SECOND_PARAM": 123
    },
)

worker, success = prt.run_task(
    file_name="task.py",          # The name of the script to run
    worker_config=worker_config,
)

print("Task finished with status:", success)
```

When this code runs, it will print out the values of `MY_FIRST_PARAM` and `MY_SECOND_PARAM` from within `task.py`.

## Airflow Integration
To integrate with Practicus AI Airflow, you can utilize the same approach. Airflow tasks can inject environment variables by writing out a `WorkerConfig` JSON file that Practicus AI can pick up.

For example:
1. Define your `worker_config` in Python.
2. Serialize it to JSON.
3. Store it in a file named after your task (e.g., `task_worker.json` if your script is `task.py`).

### Example: Writing `task_worker.json`

```python
worker_config_json = worker_config.model_dump_json(exclude_none=True)

with open("task_worker.json", "wt") as f:
    f.write(worker_config_json)

print("Generated worker_config JSON:\n", worker_config_json)
```

An example `task_worker.json` might look like:

```json
{
  "worker_image": "practicus",
  "worker_size": "X-Small",
  "additional_params": "eyJlbnZfdmFyaWFibGVzIjogeyJNWV9GSVJTVF9QQVJBTSI6ICJWQUxVRTEiLCAiTVlfU0VDT05EX1BBUkFNIjogMTIzfX0="
}
```

Note that `additional_params` is base64-encoded data containing:

```json
{
  "env_variables": {
    "MY_FIRST_PARAM": "VALUE1",
    "MY_SECOND_PARAM": 123
  }
}
```
This is how Practicus AI stores your configuration behind the scenes.

## Summary

* **Defining environment variables**: Use `env_variables` within `WorkerConfig` to inject parameters.
* **Accessing parameters**: In your Python script (e.g., `task.py`), read them from `os.environ`.
* **Airflow**: Write out the `worker_config` to a JSON file. Practicus AI automatically picks that up.

By following these steps, you can effectively pass custom parameters and configurations to your Practicus AI tasks, making your data pipelines more dynamic and flexible.


---

**Previous**: [Bank Marketing](../modeling/bank-marketing/bank-marketing.md) | **Next**: [API Triggers For Airflow](api-triggers-for-airflow.md)
