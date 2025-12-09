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
