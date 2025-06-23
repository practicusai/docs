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
    worker_size="X-Small",  # Size configuration
    env_variables={"MY_FIRST_PARAM": "VALUE1", "MY_SECOND_PARAM": 123},
)

worker, success = prt.run_task(
    file_name="task.py",  # The name of the script to run
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


## Supplementary Files

### run_task_safe/default_worker.json
```json
{"worker_image":"practicus","worker_size":"Small","service_url":"","email":"","refresh_token":""}
```

### run_task_safe/run_task_safe_dag.py
```python
# Airflow DAG run_task_safe_dag.py created using Practicus AI

import logging
from datetime import datetime
from airflow.decorators import dag, task
import practicuscore as prt
import os

# Constructing a Unique DAG ID
# ----------------------------
# We strongly recommend using a DAG ID format like:
#    <dag_key>.<username>
# This approach ensures the username effectively serves as a namespace,
#    preventing name collisions in Airflow.

# Let's locate dag_key and username. This runs in Airflow 'after' deployment.
dag_key, username = prt.workflows.get_dag_info(__file__)
dag_id = f"{dag_key}.{username}"


def convert_local(d):
    logging.debug("Converting {}".format(d))
    return d.in_timezone("Europe/Istanbul")


def _read_cloud_worker_config_from_file(worker_config_json_path: str) -> dict:
    cloud_worker_conf_dict = {}  # type: ignore[var-annotated]
    try:
        if os.path.exists(worker_config_json_path):
            prt.logger.info(f"Reading Worker config from {worker_config_json_path}")
            with open(worker_config_json_path, "rt") as f:
                content = f.read()
                import json

                cloud_worker_conf_dict = json.loads(content)
        else:
            prt.logger.info(
                f"Worker configuration file {worker_config_json_path} not found. "
                f"Airflow DAG must provide settings via params passed from run DAG UI or global Airflow configuration."
            )
    except:
        prt.logger.error(f"Could not parse Worker config from file {worker_config_json_path}", exc_info=True)
    return cloud_worker_conf_dict


def _get_worker_config_dict(**kwargs) -> dict:
    dag = kwargs["dag"]
    dag_folder = dag.folder

    final_dict = {}

    worker_config_json_path = os.path.join(dag_folder, "default_worker.json")
    prt.logger.debug(f"worker_config_json_path : {worker_config_json_path}")
    if os.path.exists(worker_config_json_path):
        worker_dict_from_json_file = _read_cloud_worker_config_from_file(worker_config_json_path)
        try:
            for key, value in worker_dict_from_json_file.items():
                if value not in [None, "", "None"]:
                    prt.logger.info(
                        f"Updating Worker configuration key '{key}' using "
                        f"task specific worker configuration file: default_worker.json"
                    )
                    final_dict[key] = value
        except:
            prt.logger.error(f"Could not parse param dictionary from {worker_config_json_path}", exc_info=True)

    return final_dict


def _cleanup(**kwargs):
    from datetime import datetime, timezone

    timeout_seconds = 59  # Threshold for considering a Worker as stuck
    _worker_config_dict = _get_worker_config_dict(**kwargs)
    region = prt.regions.region_factory(_worker_config_dict)
    prt.logger.info(f"Found region : {str(region)}")
    # Iterate through all Workers in the region
    for worker in region.worker_list:
        time_since_creation = int((datetime.now(timezone.utc) - worker.creation_time).total_seconds())
        prt.logger.info(
            f"{worker.name} started {time_since_creation} seconds ago and is currently in '{worker.status}' state."
        )
        if worker.status == "Provisioning" and time_since_creation > timeout_seconds:
            prt.logger.warning(
                f"-> Terminating {worker.name} — stuck in 'Provisioning' for more than {timeout_seconds} seconds."
            )
            worker.terminate()


# Define other DAG properties like schedule, retries etc.
@dag(
    dag_id=dag_id,
    schedule_interval=None,
    start_date=datetime(2025, 5, 9, 7, 0),
    default_args={
        "owner": username,
        "retries": 0,
    },
    catchup=False,
    user_defined_macros={"local_tz": convert_local},
    max_active_runs=1,
    params=prt.workflows.get_airflow_params(),
)
def generate_dag():
    # The `task_id` must match the task file (e.g., `my_1st_task.py or my_1st_task.sh`)
    # located in the same folder as this DAG file.
    def run_with_dynamic_param(**kwargs):
        from practicuscore.exceptions import TaskError

        try:
            return prt.workflows.run_airflow_task(**kwargs)
        except TaskError as ex:
            _cleanup(**kwargs)
            raise ex

    task1 = task(run_with_dynamic_param, task_id="task1")()

    # Define how your task will flow
    task1


generate_dag()

```

### run_task_safe/task1.py
```python
import practicuscore as prt


def main():
    prt.logger.info("Running task 1 is completed")


if __name__ == "__main__":
    main()

```

### task_runnner_app/apis/sample_callback.py
```python
# Sample callback APIs, we will use them for our tests.

from pydantic import BaseModel
import practicuscore as prt
from starlette.requests import Request


class TaskRunnerCallbackRequest(BaseModel):
    task_name: str
    """Model Deployment Task"""

    task_id: str
    """Unique task ID"""

    success: bool
    """True if the task completed successfully, False otherwise"""

    logs: str
    """Any info or error message"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "task_name": "deploy_model",
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "success": True,
                    "message": "Model deployed successfully",
                },
                {
                    "task_name": "cleanup_task",
                    "task_id": "123e4567-e89b-12d3-a456-426614174001",
                    "success": False,
                    "message": "Error occurred during cleanup",
                },
            ]
        },
    }


class TaskRunnerCallbackResponse(BaseModel):
    success: bool
    """True or False"""

    message: str
    """Any info or error message"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"success": True, "message": "Successfully finished"},
                {"success": False, "message": "Errored occurred"},
            ]
        },
    }


api_spec = prt.APISpec(
    disable_authentication=True,
)


@prt.apps.api(path="/sample-task-runner-callback", spec=api_spec)
async def task_runner_callback(payload: TaskRunnerCallbackRequest, **kwargs) -> TaskRunnerCallbackResponse:
    if payload.success:
        prt.logger.info(f"Task with name : {payload.task_name} task_id : finished successfully")
    else:
        prt.logger.error(
            f"Task with name : {payload.task_name} finished with error\npayload : {payload.model_dump_json(indent=2)}"
        )

    return TaskRunnerCallbackResponse(success=True, message="ok")


@prt.apps.api(path="/sample-task-runner-callback2", spec=api_spec)
async def task_runner_callback2(request: Request, **kwargs) -> TaskRunnerCallbackResponse:
    prt.logger.info(f"request: {request}")

    body: dict = await request.json()

    task_name = body.get("task_name")
    task_id = body.get("task_id")
    success = body.get("success")
    logs = body.get("logs")

    if success:
        prt.logger.info(f"Task with name : {task_name} task_id : {task_id} finished successfully")
    else:
        prt.logger.error(f"Task with name : {task_name} task_id : {task_id} finished with error\nlogs : {logs}")

    return TaskRunnerCallbackResponse(success=True, message="ok")

```

### task_runnner_app/apis/task_runner.py
```python
import os
import threading

import requests
from pydantic import BaseModel

import practicuscore as prt


class TaskRunnerRequest(BaseModel):
    task_id: str
    """Unique task id (1222345, 23erd-rt56-tty67-34er5 ...)"""

    task_file_name: str
    """deployer_task.py, task1.sh... (*.py, *.sh files) """

    worker_config: prt.WorkerConfig
    """WorkerConfig with or without a GitConfig"""

    callback_url: str | None = None
    """Callback URL to be called after the task finishes"""

    callback_url_token: str | None = None
    """Optional Callback URL security (bearer) token"""

    terminate_on_completion: bool = True
    """Determines whether the task runner should terminate on completion"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": "23erd-rt56",
                    "task_file_name": "deployer_task.py",
                    "worker_config": {
                        "worker_size": "small",
                        "personal_secrets": ["git_secret"],
                        "git_configs": [
                            {"remote_url": "https://github.com/example/repo.git", "secret_name": "git_secret"}
                        ],
                    },
                    "callback_url": "https://example.com/callback",
                    "terminate_on_completion": True,
                }
            ]
        },
    }


class TaskRunnerResponse(BaseModel):
    success: bool
    """True or False"""

    message: str
    """Any info or error message"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"success": True, "message": "Successfully finished"},
                {"success": False, "message": "Errored occurred"},
            ]
        },
    }


@prt.apps.api(path="/task-runner")
async def task_runner(payload: TaskRunnerRequest, **kwargs) -> TaskRunnerResponse:
    """This API starts task async and returns started message"""

    prt.logger.info("Started running task...")
    thread: threading.Thread | None = None
    try:
        thread = threading.Thread(target=run_task, args=[payload])
        thread.start()
        return TaskRunnerResponse(success=True, message="Started Task successfully")
    except Exception as ex:
        prt.logger.error("Error on task", exc_info=True)
        return TaskRunnerResponse(success=False, message=f"An Error occurred while running task. Error: {str(ex)}")


def run_task(request: TaskRunnerRequest):
    assert request.task_file_name, "No task_file_name located"
    assert request.worker_config, "No worker_config located"

    success = None
    worker = None
    worker_logs = ""
    try:
        prt.logger.info(
            f"Starting task: {request.task_id} ({request.task_file_name}) terminate_on_completion: {request.terminate_on_completion}"
        )
        tasks_path = get_tasks_path()
        prt.logger.info(f"Tasks path to upload: {tasks_path}")
        worker, success = prt.run_task(
            file_name=request.task_file_name,
            files_path=tasks_path,
            worker_config=request.worker_config,
            terminate_on_completion=False,
        )
        worker_logs = worker.get_logs(log_size_mb=5)
    except Exception as ex:
        message = f"Finished task_name: {request.task_file_name} with error"
        prt.logger.error(message, exc_info=True)
        raise ex
    finally:
        try:
            if success is not None:
                if success:
                    prt.logger.info("Finished successfully")
                else:
                    prt.logger.error(
                        f"Finished task with error. Check logs for details. task_name: {request.task_file_name}"
                    )
                if request.callback_url:
                    trigger_callback(request=request, success=success, worker_logs=worker_logs)
                else:
                    prt.logger.debug(f"Task: {request.task_file_name} does not have a callback url.")
        finally:
            if worker is not None and request.terminate_on_completion:
                worker.terminate()


def trigger_callback(request: TaskRunnerRequest, success: bool, worker_logs: str):
    request.callback_url, "No callback_url located"

    headers = {"content-type": "application/json"}
    if request.callback_url_token:
        prt.logger.debug(f"Task: '{request.task_file_name}' includes a security token, including as a Bearer token.")
        headers["authorization"] = f"Bearer {request.callback_url_token}"
    else:
        prt.logger.debug(f"Task: {request.task_file_name} does not include a security token.")

    callback_payload = {
        "task_name": request.task_file_name,
        "task_id": request.task_id,
        "success": success,
        "logs": worker_logs,
    }

    import json

    json_data = json.dumps(callback_payload)

    prt.logger.info(f"Sending to callback url: '{request.callback_url}' success: '{success}'")
    resp = requests.post(request.callback_url, json=json_data, headers=headers)

    if resp.ok:
        prt.logger.info(f"Response text: {resp.text}")
    else:
        prt.logger.error(f"Response has errors:  resp.status_code: {resp.status_code}  - resp.text{resp.text}")


def get_tasks_path() -> str:
    """
    Returns the path to the 'tasks' directory.

    Steps:
    1. Retrieve the current execution path using get_execution_path().
    2. Get the parent directory of the execution path.
    3. Construct the path to the 'tasks' directory
    """
    # Get the execution path.
    exec_path = get_execution_path()
    prt.logger.debug(f"Exec pah: {exec_path}")
    # Determine the parent directory of the execution path.
    parent_dir = os.path.dirname(exec_path)
    prt.logger.debug(f"parent_dir: {parent_dir}")
    # Construct the path for the "tasks" directory at the same level.
    path = os.path.join(parent_dir, "tasks")
    prt.logger.debug(f"path: {path}")
    return path


def get_execution_path() -> str:
    """
    Returns the execution path of the current script.
    If the __file__ variable is available, it returns the directory of the script.
    Otherwise, it falls back to the current working directory.
    """
    try:
        # __file__ is defined when the script is run from a file.
        path = os.path.dirname(os.path.abspath(__file__))
        prt.logger.debug(f"path from file path: {path}")
        return path
    except NameError:
        # __file__ is not defined in an interactive shell; use the current working directory.
        path = os.getcwd()
        prt.logger.debug(f"path from os.getcwd(): {path}")
        return path


# async def main():
#     worker_config = prt.WorkerConfig(
#         worker_size="X-Small",
#         # personal_secrets=[git_secret_name],
#         # git_configs=[git_config],
#     )

#     payload = TaskRunnerRequest(
#         task_file_name="deployer_task.py",
#         task_id="task-1",
#         worker_config=worker_config,
#         callback_url="https://dev.practicus.io/apps/task-runner-app/api/task-runner-callback",
#         terminate_on_completion=True,
#     )
#     await task_runner(payload)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(main())


# if __name__ == "__main__":
#     worker_config = prt.WorkerConfig(worker_size="X-Small")
#     payload = TaskRunnerRequest(
#         task_file_name="deployer_task.py",
#         task_id="task-1",
#         worker_config=worker_config,
#         callback_url="https://dev.practicus.io/apps/task-runner-app/api/task-runner-callback",
#         terminate_on_completion=True,
#     )

#     trigger_callback(request=payload, success=True, worker_logs="logs logs ....")

```

### task_runnner_app/tasks/deployer_task.py
```python
# Sample Task that the Task Runner App will execute

import practicuscore as prt
from pathlib import Path


def any_file_exists(dir_path: str) -> bool:
    """
    Check if there is at least one file anywhere under the given directory.

    :param dir_path: Path to the directory to be searched.
    :return: True if any file is found, False otherwise.
    """
    base = Path(dir_path)
    return any(p.is_file() for p in base.rglob("*"))


def main():
    prt.logger.info("Starting model deployment task ")

    import os

    assert "DEPLOYMENT_KEY" in os.environ and len(os.environ["DEPLOYMENT_KEY"]) > 0, "DEPLOYMENT_KEY is not provided"
    assert "PREFIX" in os.environ and len(os.environ["PREFIX"]) > 0, "PREFIX is not provided"
    assert "MODEL_NAME" in os.environ and len(os.environ["MODEL_NAME"]) > 0, "MODEL_NAME is not provided"
    assert "MODEL_DIR" in os.environ and len(os.environ["MODEL_DIR"]) > 0, "MODEL_DIR is not provided"

    deployment_key = os.environ["DEPLOYMENT_KEY"]  # "depl"
    prefix = os.environ["PREFIX"]  # models
    model_name = os.environ["MODEL_NAME"]  # sample-model-ro
    model_dir = os.environ["MODEL_DIR"]  # "/home/ubuntu/my/projects/models-repo/sample-model"

    if not any_file_exists(model_dir):
        msg = "Model directory is empty or does not exist. Check logs for details."
        prt.logger.error(msg)
        raise RuntimeError(msg)
    else:
        api_url, api_version_url, api_meta_url = prt.models.deploy(
            deployment_key=deployment_key, prefix=prefix, model_name=model_name, model_dir=model_dir
        )
        prt.logger.info(f"Finished model deployment task successfully. api_url : {api_version_url}")


if __name__ == "__main__":
    main()

```


---

**Previous**: [Build](task-runnner-app/build.md) | **Next**: [Run Task Safe > Deploy](run-task-safe/deploy.md)
