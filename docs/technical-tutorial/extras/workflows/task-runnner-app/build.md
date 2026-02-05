---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

<!-- #region -->
# Building a Task Runner App

This example walks you through the complete life‑cycle of:
- **Building an App that runs Practicus AI tasks**
- **And expose it's functionality as an API.**

**Use case**

- A remote CI/CD platform (e.g. Jenkins) detects a code commit to a Git repo.
- The CI/CD platform calls the Task Runner App API to train a model and deploy.
    - The API request includes what kind of Practicus AI Worker to use,
    - Which Git repo to pull the tasks code,
    - And a callback URL to recive the success/failure of the task.
- Task Runner App starts the Worker, and starts observing it's status.
    - The task that the Worker is executing can be complex task that involves starting other Workers in a chain.
- After the task is completed, Task Runner App calls the CI/CD platform callback url reporting on the result.


**High level overview**

1. **Parameter setup** – keep all tunables together for easy reuse.
2. **Discover existing deployment settings & prefixes** – so you never guess names.
3. **Securely integrate your Git repository** – store your Personal Access Token once and reuse it safely.
4. **Ship a new *Task Runner* app version** – build, upload, and boot the API in a single call.
5. **Trigger a background worker** – start a model‑deployment task and receive results through a callback.
6. **Clean‑up utilities** – list and delete apps or versions when they are no longer needed.

Feel free to execute each cell sequentially or jump straight to the sections most relevant to your workflow.
<!-- #endregion -->

## 1 · Define Notebook Parameters

Centralising parameters at the top keeps the rest of the notebook *read‑only* and easier to maintain. Change these two strings to use a different deployment profile or prefix.

```python
# Notebook parameters
app_deployment_key: str | None = None  # e.g. "appdepl", "langflow-app-depl", ...
app_prefix: str = "apps"  # e.g. "apps", "apps-finance", ...
```

```python
# Sanity checks – fail early if a parameter is missing
assert app_deployment_key, "Please set 'app_deployment_key' above."
assert app_prefix, "Please set 'app_prefix' above."
```

## 2 · Discover Available Deployment Settings & Prefixes

Use the Practicus AI SDK to list *only* the settings you have permission to see. This helps avoid typos and speeds up onboarding for new team‑mates.

```python
import practicuscore as prt

# Connect to the default region configured on this workstation
region = prt.get_region()

# List deployment settings that can host our app
print("Deployment settings available to you:")
display(region.app_deployment_setting_list.to_pandas())

# List logical prefixes (a.k.a app groups) you can deploy into
print("App prefixes available to you:")
display(region.app_prefix_list.to_pandas())
```

## 3 · Integrate Your Git Repository Securely

A **Personal Access Token (PAT)** is saved in the Practicus AI Vault only once. Subsequent executions simply reuse the stored secret.

```python
from getpass import getpass
import practicuscore as prt

git_secret_name: str = "MY_GIT_SECRET"  # change if you prefer another secret id
```

```python
# Prompt (only once) and persist the PAT into Practicus AI Vault ----------
try:
    token = getpass("Enter your Git personal access token (press Enter to skip if already saved): ")
    if token:
        prt.vault.create_or_update_secret(name=git_secret_name, key=token)
        print(f"Secret '{git_secret_name}' stored/updated successfully.")
except Exception as exc:
    print("Could not store secret:", exc)
```

## 4 · Deploy the Task‑Runner App

We now deploy (or update) an application called **`task-runner-app`** under our chosen prefix. The SDK automatically creates a new *version* each time the code changes.

```python
app_name = "task-runner-app"  # DNS‑safe name
visible_name = "Task Runner API"  # UI label
description = "Starts background model-related tasks"
icon = "fa-rocket"  # FontAwesome icon

# Kick off the deployment -------------------------------------------------
app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,  # current working directory by default
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("UI    :", app_url)
print("API   :", api_url)

# NOTE ▸ The cell blocks until the new version is ready and reachable.
```

## 5 · Build a Worker Configuration & Task Payload

A *Task Runner* requires a **`WorkerConfig`** (resources, environment variables, Git repo, etc.) and a small **payload** describing what to execute. Below we clone a model repository, set essential environment variables, and tell the worker to run `deployer_task.py`.

```python
from apis.task_runner import TaskRunnerRequest, TaskRunnerResponse
import practicuscore as prt

# ---------------------------------------------------------------------------
# Git integration for the worker
# ---------------------------------------------------------------------------
remote_url = "https://github.com/your-org/your-model-repo.git"
git_config = prt.GitConfig(remote_url=remote_url, secret_name=git_secret_name)

# ---------------------------------------------------------------------------
# Worker specification
# ---------------------------------------------------------------------------
worker_config = prt.WorkerConfig(
    worker_size="X-Small",
    git_configs=[git_config],
    personal_secrets=[git_secret_name],  # mount the PAT so cloning works
    env_variables={  # parameters consumed by the task
        "DEPLOYMENT_KEY": "depl2",
        "PREFIX": "models",
        "MODEL_NAME": "sample-model",
        "MODEL_DIR": "/path/on/worker/sample-model",  # edit as needed
    },
)

# ---------------------------------------------------------------------------
# Create TaskRunner request payload
# ---------------------------------------------------------------------------
payload = TaskRunnerRequest(
    task_id="model-deployment-task-1",
    task_file_name="deployer_task.py",
    worker_config=worker_config,
    callback_url=f"{api_url}task-runner-callback",
    terminate_on_completion=False,  # keep worker alive for debugging
)
```

## 6 · Kick Off the Task & Inspect the Response

We authenticate against the freshly‑deployed API, send the payload as JSON, and parse the structured response back into a Pydantic model for convenience.

```python
import json
import requests

# Obtain a short‑lived session token for the new API ----------------------
token = prt.apps.get_session_token(api_url=api_url)
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

task_runner_endpoint = f"{api_url}task-runner/"
print("POSTing TaskRunner payload to:", task_runner_endpoint)

# Convert Pydantic model → dict → JSON for readability (indent=2) ----------
json_payload = json.loads(payload.model_dump_json())
print(json.dumps(json_payload, indent=2))

response = requests.post(task_runner_endpoint, json=json_payload, headers=headers)

if response.ok:
    parsed = TaskRunnerResponse.model_validate_json(response.text)
    print("\n✅ Task accepted →", parsed.message)
else:
    print("\n❌ Error:", response.status_code, response.text)
```

## 7 · Maintenance & Clean‑Up Utilities

Admins or app owners can list, delete, or prune old versions directly from code. **Never** delete the latest version while it is still serving production traffic.

```python
# List every app you can see in this region --------------------------------
print("Apps and versions visible to you:")
display(region.app_list.to_pandas())
```

```python
# Delete an entire app (all versions) – requires ownership or admin rights --
try:
    region.delete_app(prefix=app_prefix, app_name=app_name)  # safer than raw app_id
    print(f"Deleted app '{app_prefix}/{app_name}'.")
except Exception as exc:
    print("Delete failed (possibly no permission or already gone):", exc)
```

```python
# Delete a *single* version (cannot be the latest) -------------------------
try:
    region.delete_app_version(prefix=app_prefix, app_name=app_name, version=4)
    print("Version 4 removed.")
except Exception as exc:
    print("Delete version failed:", exc)
```


## Supplementary Files

### apis/sample_callback.py
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

### apis/task_runner.py
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
#         callback_url="https://practicus.company.com/apps/task-runner-app/api/task-runner-callback",
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
#         callback_url="https://practicus.company.com/apps/task-runner-app/api/task-runner-callback",
#         terminate_on_completion=True,
#     )

#     trigger_callback(request=payload, success=True, worker_logs="logs logs ....")

```

### tasks/deployer_task.py
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

**Previous**: [Task Parameters](../task-parameters.md) | **Next**: [Generative AI > Agentic Use Cases > Growth Strategist > Build](../../generative-ai/agentic-use-cases/growth-strategist/build.md)
