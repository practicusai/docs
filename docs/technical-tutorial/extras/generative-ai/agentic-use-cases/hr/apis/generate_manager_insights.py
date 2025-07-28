# apis/generate_manager_insights.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal."""

    rationale: str
    """Explanation of why this signal was detected."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    risk_level: str
    """Burnout risk label (e.g. 'High', 'Medium', 'Low', 'None')."""

    justification: str
    """Justification for the assigned risk level."""


class ManagerInsight(BaseModel):
    employee_id: str
    """The employee for whom the insight is generated."""

    summary: str
    """A brief summary of the employee's current behavioral and risk profile."""

    advice: str
    """Suggested action or communication approach for the manager."""

    development_hint: str
    """Optional development recommendation tailored to the employee."""


class GenerateManagerInsightsRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals for each employee."""

    risks: List[BurnoutRisk]
    """List of burnout risk assessments."""


class GenerateManagerInsightsResponse(BaseModel):
    insights: List[ManagerInsight]
    """Personalized insight reports per employee for the manager."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-manager-insights", spec=api_spec)
async def run(payload: GenerateManagerInsightsRequest, **kwargs) -> GenerateManagerInsightsResponse:
    """
    Generates personalized and actionable insights for managers based on behavioral signals and burnout risks,
    helping them guide, coach, or support each employee effectively.
    """
    dummy = ManagerInsight(
        employee_id=payload.signals[0].employee_id,
        summary="Employee shows signs of fatigue and inconsistency.",
        advice="Schedule a 1-on-1 to discuss workload and recent challenges. Maintain a supportive tone.",
        development_hint="Consider offering time management coaching or mentoring."
    )

    return GenerateManagerInsightsResponse(insights=[dummy])
