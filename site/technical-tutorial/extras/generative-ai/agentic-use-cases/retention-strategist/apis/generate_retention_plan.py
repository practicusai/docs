# generate_retention_plan.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class RetentionTarget(BaseModel):
    customer_id: str
    """ID of the customer who is at churn risk."""

    churn_risk: str
    """Level of churn risk: low, medium, or high."""

    loyalty_score: Optional[float]
    """Predicted loyalty score from the model."""

    complaint_topic: Optional[str]
    """Dominant complaint topic extracted from feedbacks."""

    sentiment: Optional[str]
    """Overall customer sentiment, if known."""

    model_config = {
        "use_attribute_docstrings": True
    }


class RetentionPlan(BaseModel):
    customer_id: str
    """ID of the customer for whom the plan is generated."""

    plan_summary: str
    """Natural language recommendation plan to retain the customer."""

    model_config = {
        "use_attribute_docstrings": True
    }


class GenerateRetentionPlanResponse(BaseModel):
    plans: List[RetentionPlan]
    """Generated action plans to reduce churn likelihood per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "plans": [
                        {
                            "customer_id": "C033",
                            "plan_summary": "Customer C033 exhibits high churn risk due to support delays and negative sentiment. Recommend assigning a dedicated account manager, offering priority support, and a goodwill credit to rebuild trust."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Medium
)


@prt.api("/generate-retention-plan", spec=api_spec)
async def run(targets: List[RetentionTarget], **kwargs) -> GenerateRetentionPlanResponse:
    """
    Creates LLM-generated retention plans based on churn risk and behavior signals.
    """

    plans = []

    for target in targets:
        recs = []

        if target.churn_risk == "high":
            recs.append("assign a dedicated account manager")
        if target.complaint_topic:
            recs.append(f"resolve recent issues around {target.complaint_topic}")
        if target.sentiment == "negative":
            recs.append("provide a goodwill gesture such as a discount or credit")
        if target.loyalty_score is not None and target.loyalty_score < 0.5:
            recs.append("initiate re-engagement campaign with personalized offers")

        plan = (
            f"Customer {target.customer_id} exhibits {target.churn_risk} churn risk"
        )
        if target.complaint_topic or target.sentiment:
            plan += f" possibly due to {target.complaint_topic or target.sentiment}"
        plan += f". Recommend to " + ", ".join(recs) + "."

        plans.append(RetentionPlan(customer_id=target.customer_id, plan_summary=plan))

    return GenerateRetentionPlanResponse(plans=plans)
