# apis/generate_customer_summary.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class CustomerSignal(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    loyalty_score: Optional[float]
    """Predicted loyalty score based on engagement and sentiment."""

    churn_risk: Optional[str]
    """Level of churn risk: low, medium, or high."""

    dominant_complaint_topic: Optional[str]
    """Most frequently detected complaint topic, if any."""

    feedback_sentiment: Optional[str]
    """Overall sentiment from feedback data (e.g., positive, neutral, negative)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C021",
                    "loyalty_score": 0.82,
                    "churn_risk": "low",
                    "dominant_complaint_topic": "billing",
                    "feedback_sentiment": "positive"
                }
            ]
        }
    }


class GenerateCustomerSummaryRequest(BaseModel):
    signals: List[CustomerSignal]
    """Customer-level prediction outputs and behavioral insights."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "signals": [
                        {
                            "customer_id": "C021",
                            "loyalty_score": 0.82,
                            "churn_risk": "low",
                            "dominant_complaint_topic": "billing",
                            "feedback_sentiment": "positive"
                        }
                    ]
                }
            ]
        }
    }


class CustomerSummary(BaseModel):
    customer_id: str
    """The customer the summary is about."""

    summary: str
    """Plain English summary of customer's status and risk profile."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C021",
                    "summary": "Customer C021 has loyalty score of 0.82, low churn risk, positive recent feedback, notable complaints around billing."
                }
            ]
        }
    }


class GenerateCustomerSummaryResponse(BaseModel):
    summaries: List[CustomerSummary]
    """List of summaries for each customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summaries": [
                        {
                            "customer_id": "C021",
                            "summary": "Customer C021 has loyalty score of 0.82, low churn risk, positive recent feedback, notable complaints around billing."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True
)


@prt.api("/generate-customer-summary", spec=api_spec)
async def run(payload: GenerateCustomerSummaryRequest, **kwargs) -> GenerateCustomerSummaryResponse:
    """
    Generates plain English summaries of individual customers based on risk and engagement data.
    """

    summaries = []

    for signal in payload.signals:
        parts = []

        if signal.loyalty_score is not None:
            parts.append(f"loyalty score of {signal.loyalty_score:.2f}")
        if signal.churn_risk:
            parts.append(f"{signal.churn_risk} churn risk")
        if signal.feedback_sentiment:
            parts.append(f"{signal.feedback_sentiment} recent feedback")
        if signal.dominant_complaint_topic:
            parts.append(f"notable complaints around {signal.dominant_complaint_topic}")

        summary = f"Customer {signal.customer_id} has " + ", ".join(parts) + "."
        summaries.append(CustomerSummary(customer_id=signal.customer_id, summary=summary))

    return GenerateCustomerSummaryResponse(summaries=summaries)
