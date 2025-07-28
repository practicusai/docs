# apis/calculate_team_resilience.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class TeamBehaviorSignal(BaseModel):
    employee_id: str
    """The ID of the employee."""

    team: str
    """Team name the employee belongs to."""

    signal: str
    """Short label of behavioral pattern."""

    rationale: str
    """Explanation of the signal."""


class TeamResilienceScore(BaseModel):
    team: str
    """Team name."""

    resilience_level: str
    """Estimated resilience level: High, Medium, Low."""

    explanation: str
    """Explanation of the score assigned."""

    improvement_advice: str
    """Suggested interventions to improve resilience."""


class CalculateTeamResilienceRequest(BaseModel):
    signals: List[TeamBehaviorSignal]
    """Team-wide behavioral signals."""


class CalculateTeamResilienceResponse(BaseModel):
    scores: List[TeamResilienceScore]
    """Resilience scores per team."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/calculate-team-resilience", spec=api_spec)
async def run(payload: CalculateTeamResilienceRequest, **kwargs) -> CalculateTeamResilienceResponse:
    """
    Evaluates the resilience level of teams based on behavioral patterns, providing strategic guidance
    on how to strengthen adaptability and cohesion during stress or change.
    """
    dummy = TeamResilienceScore(
        team=payload.signals[0].team,
        resilience_level="Medium",
        explanation="Team shows moderate fluctuation under pressure. Some members display warning signs during tight deadlines.",
        improvement_advice="Introduce stress-coping workshops and team retrospectives to improve trust and adaptability."
    )

    return CalculateTeamResilienceResponse(scores=[dummy])
