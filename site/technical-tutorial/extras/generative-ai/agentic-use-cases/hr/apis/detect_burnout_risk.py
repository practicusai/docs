# apis/detect_burnout_risk.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal (e.g. 'Burnout Risk')."""

    rationale: str
    """Explanation of why this signal was detected based on behavioral history."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    risk_level: str
    """Risk category (e.g. 'High', 'Medium', 'Low', 'None')."""

    justification: str
    """LLM-generated justification for the burnout risk classification."""


class DetectBurnoutRiskRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of extracted behavioral signals for each employee."""


class DetectBurnoutRiskResponse(BaseModel):
    risks: List[BurnoutRisk]
    """Burnout risk levels determined for employees, with explanations."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/detect-burnout-risk", spec=api_spec)
async def run(payload: DetectBurnoutRiskRequest, **kwargs) -> DetectBurnoutRiskResponse:
    """
    Analyzes behavioral signals using LLM reasoning to identify employees at potential risk of burnout,
    categorizing them as High, Medium, Low, or None with proper justification.
    """
    # Dummy dönüş (gerçek risk analizi zincirde yapılacak)
    dummy_risk = BurnoutRisk(
        employee_id=payload.signals[0].employee_id,
        risk_level="High",
        justification="Combination of negative feedback, fluctuating performance and repeated absences."
    )

    return DetectBurnoutRiskResponse(risks=[dummy_risk])
