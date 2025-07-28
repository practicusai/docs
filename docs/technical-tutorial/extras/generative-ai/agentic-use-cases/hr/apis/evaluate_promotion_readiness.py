# apis/evaluate_promotion_readiness.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal (e.g. 'Consistent Performer')."""

    rationale: str
    """Explanation of why this signal was detected based on behavioral history."""


class PromotionAssessment(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    readiness_level: str
    """Promotion readiness label (e.g. 'Ready', 'Needs Development', 'Not Ready')."""

    justification: str
    """LLM-generated justification explaining why the employee was classified at this level."""


class EvaluatePromotionReadinessRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals derived from previous analysis."""


class EvaluatePromotionReadinessResponse(BaseModel):
    promotion_recommendations: List[PromotionAssessment]
    """List of promotion readiness levels with justifications."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/evaluate-promotion-readiness", spec=api_spec)
async def run(payload: EvaluatePromotionReadinessRequest, **kwargs) -> EvaluatePromotionReadinessResponse:
    """
    Evaluates employees' readiness for promotion based on detected behavioral signals,
    and provides a recommendation with reasoning.
    """
    dummy_assessment = PromotionAssessment(
        employee_id=payload.signals[0].employee_id,
        readiness_level="Ready",
        justification="Employee has shown consistent performance, strong communication, and proactive leadership."
    )

    return EvaluatePromotionReadinessResponse(
        promotion_recommendations=[dummy_assessment]
    )
