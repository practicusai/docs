# apis/summarize_customer_retention_case.py
import practicuscore as prt
from pydantic import BaseModel


class SummarizeCustomerRetentionCaseRequest(BaseModel):
    customer_id: str
    """Unique identifier of the customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"customer_id": "C105"}]},
    }


class SummarizeCustomerRetentionCaseResponse(BaseModel):
    summary: str
    """High-level summary of the customer's retention case, including risks and suggested actions."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Customer C105 has shown declining engagement and expressed dissatisfaction. Retention plan recommended."
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/summarize-customer-retention-case", spec=api_spec)
async def run(payload: SummarizeCustomerRetentionCaseRequest, **kwargs) -> SummarizeCustomerRetentionCaseResponse:
    """
    Summarizes the current retention case for a given customer, including behavioral patterns, sentiment signals,
    and recommended actions if relevant.
    """
    return SummarizeCustomerRetentionCaseResponse(
        summary=f"Customer {payload.customer_id} has shown declining engagement and expressed dissatisfaction. Retention plan recommended."
    )
