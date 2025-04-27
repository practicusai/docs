from pydantic import BaseModel
import practicuscore as prt


class Person(BaseModel):
    name: str
    """Name of the Person"""
    email: str | None = None
    """Email of the Person"""

    model_config = {
        "use_attribute_docstrings": True,
    }


class SayHelloRequest(BaseModel):
    person: Person
    """Person to say hello to"""

    # Optional configuration
    model_config = {
        # use_attribute_docstrings=True allows documentation with """add docs here""" format
        # Alternative is to use Field(..., description="add docs here"
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            # Examples get documented in OpenAPI and are extremely useful for AI Agents.
            "examples": [
                {"person": {"name": "Alice", "email": "alice@wonderland.com"}},
                {"person": {"name": "Bill", "email": "bill@wonderland.com"}},
            ]
        },
    }


class SayHelloResponse(BaseModel):
    greeting_message: str
    """Greeting message"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"greeting_message": "Hello Alice"}, {"greeting_message": "Hello Bill"}]},
    }


@prt.api("/say-hello")
async def say_hello(payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """This API sends a greeting message back to the caller"""

    return SayHelloResponse(greeting_message=f"Hello {payload.person.name}")


# An API example custom spec (metadata)
# These get documented in OpenAPI (Swagger) format and can be made available dynamically to AI Agents
api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.AIAgent,
    read_only=False,
    scope=prt.APIScope.TeamWide,
    risk_profile=prt.APIRiskProfile.High,
    human_gated=True,
    deterministic=False,
    idempotent=False,
    stateful=True,
    asynchronous=True,
    maturity_level=4,
    disable_authentication=True,
    # Primitive types (int, str etc) are recommended for custom attributes.
    custom_attributes={
        "my-cust-attr-str": "hello",
        "my-cust-attr-int": 123,
        "my-cust-attr-float": 1.2,
        "my-cust-attr-bool": True,
    },
)


@prt.api("/say-hello-with-spec", spec=api_spec)
async def say_hello_with_spec(request, payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """
    This API does some pretty cool stuff. I'd like to explain further. But let's park for now.
    """
    return SayHelloResponse(greeting_message=f"Hello2 {payload.person.name}")
