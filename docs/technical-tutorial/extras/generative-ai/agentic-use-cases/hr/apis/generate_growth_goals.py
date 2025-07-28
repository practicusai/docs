# apis/generate_growth_goals.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the detected behavioral pattern."""

    rationale: str
    """Explanation of why this signal was identified."""


class GrowthGoal(BaseModel):
    employee_id: str
    """The employee for whom the growth goal is generated."""

    goal_title: str
    """Short and actionable growth objective (e.g., 'Improve Time Management')."""

    goal_reasoning: str
    """Explanation of why this specific growth goal was chosen."""

    followup_tip: str
    """Practical suggestion for monitoring or encouraging this goal."""


class GenerateGrowthGoalsRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavior signals to analyze for goal generation."""


class GenerateGrowthGoalsResponse(BaseModel):
    goals: List[GrowthGoal]
    """Generated growth goals for each employee with reasoning."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-growth-goals", spec=api_spec)
async def run(payload: GenerateGrowthGoalsRequest, **kwargs) -> GenerateGrowthGoalsResponse:
    """
    Uses behavioral insights to generate personalized growth goals for employees,
    helping managers support their development with clear objectives and follow-ups.
    """
    dummy = GrowthGoal(
        employee_id=payload.signals[0].employee_id,
        goal_title="Improve Time Management",
        goal_reasoning="The employee showed signs of deadline stress and inconsistent task delivery.",
        followup_tip="Suggest weekly check-ins and a self-planned task board."
    )

    return GenerateGrowthGoalsResponse(goals=[dummy])
