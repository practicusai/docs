# apis/convert_to_uppercase.py
import practicuscore as prt
from pydantic import BaseModel


class ConvertToUppercaseRequest(BaseModel):
    text: str
    """The text to be converted to uppercase."""

    model_config = {"use_attribute_docstrings": True, "json_schema_extra": {"examples": [{"text": "hello world"}]}}


class ConvertToUppercaseResponse(BaseModel):
    uppercase_text: str
    """The text converted to uppercase."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"uppercase_text": "HELLO WORLD"}]},
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/convert-to-uppercase", spec=api_spec)
async def run(payload: ConvertToUppercaseRequest, **kwargs) -> ConvertToUppercaseResponse:
    """Convert the provided text to uppercase."""
    return ConvertToUppercaseResponse(uppercase_text=payload.text.upper())
