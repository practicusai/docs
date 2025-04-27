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

# Airflow HTTP Sensor Demo

## Introduction
### What Are Airflow Sensors?
In Apache Airflow, **Sensors** are special tasks that **wait** for an external condition to be true before allowing your DAG (Directed Acyclic Graph) to proceed.

A classic use case is waiting for a file to appear on AWS S3, or for a certain row in a database table. Once the condition is met (the file exists or the row is found), the sensor task signals success, and the rest of the DAG can continue.

### Why Use an HTTP Sensor?
With **microservices** and modern architectures, you often have external services or APIs orchestrating data readiness. Instead of making Airflow directly query your database (which can load your Airflow infrastructure), you can expose an **API endpoint** that quickly checks the condition, and have Airflow poll that endpoint.

- **Offload Airflow Load**: Instead of Airflow running big queries, your microservice does the heavy lifting, and Airflow just queries the result of that check.
- **API-Driven**: Microservices can handle the domain logic, scaling, and performance. Airflow simply polls an HTTP endpoint.
- **Clean Separation of Concerns**: Airflow focuses on workflow orchestration, not on large or complex business logic.

### How This Example Helps
- **Step-by-Step Guide**: Shows how to create a simple API with a sensor route.
- **Deploy** the API so that Airflow can poll it.
- **Configure** an Airflow connection and create a DAG that uses an HTTP Sensor.

Let's jump in!


<!-- #region -->
# Airflow Sensors

For more info on HTTP sensor:
[Airflow HTTP Sensor Documentation](https://airflow.apache.org/docs/apache-airflow-providers-http/4.13.3/_api/airflow/providers/http/sensors/http/index.html)

## Create an API
Create `sensor.py` under `app/apis` folder.

```python
# app/apis/sensor.py
from starlette.requests import Request
import practicuscore as prt


@prt.apps.api("/sensor")
async def sensor(request: Request, **kwargs):
    table_name = request.query_params.get("table_name", None)
    assert table_name, "API request does not have table_name parameter, e.g. ../?table_name=my_table"

    # Add your condition, e.g. SQL query, business logic, etc.
    # If the condition is met for table_1, return True.
    # Otherwise, return False with an error message.

    if table_name == "table_1":
        return {
            "ok": True,
        }
    
    return {
        "ok": False,
        "error": f"table_name is '{table_name}' but must be 'table_1'",
    }
```

### Multiple Sensors
To create multiple sensors, you can:
- Add additional conditions and routes in the same `sensor.py`, or
- Create multiple `.py` files, each implementing a different sensor.

## Deploy the API
<!-- #endregion -->

### Notebook Parameters
Below, we define notebook parameters for selecting which deployment setting, prefix, and Airflow service to use.
Adjust these values as needed.

```python
# Parameters
# Select the app deployment setting and prefix for the API
app_deployment_key = None
app_prefix = None

# Airflow Service to use
airflow_service_key = None
token = None  # Replace with your long-term token
```

```python
assert app_deployment_key, "No app deployment setting selected."
assert app_prefix, "No app prefix selected."
assert airflow_service_key, "No Airflow service selected."
assert token, "Please assign the token for the App API you just deployed"
```

```python
import practicuscore as prt
```

### Deploying the App
The next code cell deploys our sensor API to your chosen environment (via PracticusCore).

```python
app_name = "http-sensor-test"
visible_name = "Http Sensor Test"
description = "API to test Airflow Sensors"
icon = "fa-wifi"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir="app",
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("Booting UI :", app_url)
print("Booting API:", api_url)
```

## Get a Long-Term Access Token for the API
- You need to be an **admin** for this operation.
- **Admin Console → App Hosting → Access Tokens → Create New**
  - Select an expiry date.
  - In the "App Access Tokens" section, select **http-sensor-test**.
- Copy the **app API token**. We'll paste it in the next cell.


### Test the API
It's always a good idea to test the API before hooking it into Airflow.

```python
import requests

# api_url is the base we will save in Airflow connection
sensor_api_url = api_url + "sensor/"  # The specific endpoint for the sensor

# Optional parameters
params = {"table_name": "table_1"}

headers = {
    "Authorization": f"Bearer {token}",
}

# Make a GET request to test
resp = requests.get(sensor_api_url, headers=headers, params=params)

if resp.ok:
    print("Response text:")
    print(resp.text)
    resp_dict = resp.json()
    error = resp_dict.get("error")
    if error:
        print("API returned error:", error)
    print("ok?", resp_dict.get("ok"))
else:
    print("Error:", resp.status_code, resp.text)
```

## Create a New Airflow Connection

1. Go to the **Airflow UI** → **Admin** → **Connections**.
2. Create a new connection:
   - **Conn ID**: `http_sensor_test`
   - **Conn Type**: HTTP
   - **Host**: The base URL of your deployed app. For example:
     - `https://practicus.your-company.com/apps/http-sensor-test/api/v1/` (or `/api/` without /v1/)
     - Do **not** include `sensor/` here—only the base path.
   - **Password**: Paste the **token** from above.
3. Leave other fields empty or default.

## Create the DAG
Below, we'll generate the basic DAG structure using `practicuscore`. We'll then customize it to add an HTTP Sensor.

```python
import practicuscore as prt

# Define a DAG flow with 2 tasks, one waiting for the API and one processing
dag_flow = "wait_for_api >> my_task"

# Default worker configuration
default_worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="X-Small",
)

dag_key = "http_sensor"
schedule_interval = None  # You can set a cron string or '@daily' if desired
retries = 0  # 0 for dev/test, increase for production usage

prt.workflows.generate_files(
    dag_key=dag_key,
    dag_flow=dag_flow,
    files_path=None,
    default_worker_config=default_worker_config,
    save_credentials=True,
    overwrite_existing=False,
    schedule_interval=schedule_interval,
    retries=retries,
)
```

- You can delete the generated file `wait_for_api.py`, because we'll replace it with our **sensor** code.
- Update **`http_sensor_dag.py`** so it looks like this:


```python
# http_sensor_dag.py

from datetime import datetime
from airflow.decorators import dag, task
import practicuscore as prt

# Constructing a Unique DAG ID
# ----------------------------
# We strongly recommend using a DAG ID format like:
#    <dag_key>.<username>
# This approach ensures the username effectively serves as a namespace,
# preventing name collisions in Airflow.

# Let's locate dag_key and username. This runs in Airflow 'after' deployment.
dag_key, username = prt.workflows.get_dag_info(__file__)
dag_id = f"{dag_key}.{username}"

# Fetch Bearer Token of API from Airflow Connection
from airflow.hooks.base import BaseHook

http_conn_id = "http_sensor_test"
connection = BaseHook.get_connection(http_conn_id)
bearer_token = connection.password


def check_api_response(response) -> bool:
    """Decides if the API response meets the condition to proceed."""
    # Convert response to a dictionary
    resp_dict = response.json()
    error = resp_dict.get("error")
    if error:
        print("Sensor criteria not met:", error)
    # Return True if "ok" is True, otherwise False
    return resp_dict.get("ok", False) is True


@dag(
    dag_id=dag_id,
    schedule_interval=None,  # Only run on-demand
    start_date=datetime(2025, 1, 30, 20, 13),
    default_args={
        "owner": username,
        "retries": 0,
    },
    catchup=False,
    params=prt.workflows.get_airflow_params(),
)
def generate_dag():
    from airflow.providers.http.sensors.http import HttpSensor

    wait_for_api = HttpSensor(
        task_id="wait_for_http_sensor",
        http_conn_id=http_conn_id,
        endpoint="sensor/",  # appended to the base URL in the Airflow connection
        request_params={
            "table_name": "table_1",
        },
        headers={
            "Authorization": f"Bearer {bearer_token}",
        },
        response_check=check_api_response,  # A function to validate the response
        deferrable=True,  # If True, it keeps trying until poke_interval or timeout
        poke_interval=10,  # Check every 10 seconds
        timeout=30 * 60,  # Stop after 30 minutes
    )

    my_task = task(prt.workflows.run_airflow_task, task_id="my_task")()
    wait_for_api >> my_task


generate_dag()
```

### Deploy the Workflow
Now let's deploy the workflow (i.e., the DAG) to Airflow.

```python
# Let's deploy the workflow
# Make sure service_key is defined above.

prt.workflows.deploy(
    service_key=airflow_service_key,  # corrected variable name
    dag_key=dag_key,
    files_path=None,  # Current dir
)
```

## Testing on Airflow

1. Go to your Airflow UI, enable the **http_sensor** DAG.
2. Trigger the DAG manually.
3. Observe that **wait_for_http_sensor** attempts to call the `sensor/` endpoint.
   - If the response is `ok: True`, the DAG moves to `my_task`.
   - If the response is `ok: False`, the sensor will **keep checking** at `poke_interval` until `timeout`.
4. If `table_name` is not `table_1` in the example, you’ll see an error in the logs, and the sensor won't succeed.

Try updating your `sensor.py` logic to always fail—this will let you see that `my_task` never runs, and the sensor eventually times out.

**That’s it!** You now have an Airflow DAG that uses an HTTP Sensor to poll your microservice for some condition (in this case, the existence or readiness of `table_1`).



## Supplementary Files

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

**Previous**: [Task Parameters](task-parameters.md) | **Next**: [Generative AI > Databases > Using Databases](../generative-ai/databases/using-databases.md)
