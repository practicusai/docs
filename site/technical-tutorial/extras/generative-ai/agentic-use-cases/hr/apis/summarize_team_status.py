# apis/summarize_team_status.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the detected behavioral signal."""

    rationale: str
    """Explanation of why this signal was identified."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """The employee for whom burnout risk is assessed."""

    risk_level: str
    """Risk level classification such as 'High', 'Medium', 'Low', or 'None'."""

    justification: str
    """Justification for the assigned burnout risk level."""


class TeamSummary(BaseModel):
    team_name: str
    """Name of the team this summary is about."""

    health_summary: str
    """General overview of the team's behavioral state and trends."""

    risk_distribution: str
    """Summary of burnout risk levels across team members (e.g., '3 High, 2 Medium, 4 Low')."""

    key_recommendation: str
    """Most important managerial action recommended for the team."""


class SummarizeTeamStatusRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals detected for all employees."""

    risks: List[BurnoutRisk]
    """List of burnout risk evaluations for all employees."""


class SummarizeTeamStatusResponse(BaseModel):
    summaries: List[TeamSummary]
    """Team-level summaries containing health insights and risk overviews."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/summarize-team-status", spec=api_spec)
async def run(payload: SummarizeTeamStatusRequest, **kwargs) -> SummarizeTeamStatusResponse:
    """
    Aggregates behavioral signals and burnout risks across employees to create a concise team-level health summary.
    Provides managers with strategic insights and recommendations for action.
    """
    dummy = TeamSummary(
        team_name="Marketing",
        health_summary="The team shows signs of growing fatigue and inconsistent performance.",
        risk_distribution="2 High, 3 Medium, 1 Low",
        key_recommendation="Redistribute workload, conduct check-ins, and rotate responsibilities to avoid burnout clusters."
    )

    return SummarizeTeamStatusResponse(summaries=[dummy])
