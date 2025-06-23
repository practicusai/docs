# apis/say_hello.py
import practicuscore as prt
from enum import Enum

from pydantic import BaseModel, Field


class HelloType(str, Enum):
    NORMAL = "NORMAL"
    CHEERFUL = "CHEERFUL"
    SAD = "SAD"


class SayHelloRequest(BaseModel):
    name: str
    """This is the name of the person"""

    email: str | None = Field(None, description="This is the email")

    hello_type: HelloType = HelloType.NORMAL
    """What kind of hello shall I tell"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"name": "Alice", "email": "alice@wonderland.com"},
                {"name": "Bob", "hello_type": "CHEERFUL", "email": "bob@wonderland.com"},
            ]
        },
    }


class SayHelloResponse(BaseModel):
    greeting_message: str
    """This is the greeting message"""

    name: str
    """Which person we greeted"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"greeting_message": "Hello Alice", "name": "Alice"},
                {"greeting_message": "Hello Bob!!", "name": "Bob"},
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/say-hello", spec=api_spec)
async def run(payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """Says hello to the selected user with the selected tone."""

    if payload.hello_type == HelloType.NORMAL:
        return SayHelloResponse(greeting_message=f"Hello {payload.name}", name=payload.name)
    if payload.hello_type == HelloType.CHEERFUL:
        return SayHelloResponse(greeting_message=f"Hello {payload.name}!!", name=payload.name)
    if payload.hello_type == HelloType.SAD:
        return SayHelloResponse(greeting_message=f"Hello {payload.name} :(", name=payload.name)

    raise ValueError(f"Unknown hello type {payload.hello_type}")
