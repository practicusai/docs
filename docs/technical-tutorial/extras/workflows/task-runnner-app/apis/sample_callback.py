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
