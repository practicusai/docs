# apis/detect_attrition_risk.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label of detected behavioral trend."""

    rationale: str
    """Explanation of why this signal was detected."""


class AttritionRisk(BaseModel):
    employee_id: str
    """ID of the employee being evaluated for attrition risk."""

    risk_level: str
    """Predicted risk level of voluntary attrition: High, Medium, Low, or None."""

    justification: str
    """LLM-generated explanation for the assigned risk level."""


class DetectAttritionRiskRequest(BaseModel):
    signals: List[BehaviorSignal]
    """Behavioral signals used to assess attrition likelihood."""


class DetectAttritionRiskResponse(BaseModel):
    risks: List[AttritionRisk]
    """Attrition risk evaluations for each employee."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/detect-attrition-risk", spec=api_spec)
async def run(payload: DetectAttritionRiskRequest, **kwargs) -> DetectAttritionRiskResponse:
    """
    Predicts the likelihood of employee attrition based on behavioral patterns,
    providing risk levels and reasoning to help prevent unexpected turnover.
    """
    dummy = AttritionRisk(
        employee_id=payload.signals[0].employee_id,
        risk_level="High",
        justification="Employee has shown signs of disengagement, missed growth expectations, and high absenteeism."
    )

    return DetectAttritionRiskResponse(risks=[dummy])
