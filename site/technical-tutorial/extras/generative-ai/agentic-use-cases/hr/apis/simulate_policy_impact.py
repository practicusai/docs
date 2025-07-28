# apis/simulate_policy_impact.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Detected behavioral pattern."""

    rationale: str
    """Explanation of why this signal was identified."""


class PolicyChangeProposal(BaseModel):
    title: str
    """Title of the policy or action proposal."""

    description: str
    """Detailed description of what the change will involve."""


class PolicyImpactAssessment(BaseModel):
    expected_outcome: str
    """Overall prediction of how the team will react to this policy change."""

    risks: List[str]
    """Potential negative consequences or resistance areas."""

    opportunities: List[str]
    """Potential benefits or performance gains."""

    implementation_advice: str
    """Suggestions for how to apply the policy with minimal friction."""


class SimulatePolicyImpactRequest(BaseModel):
    signals: List[BehaviorSignal]
    """Current behavioral signals to contextualize the simulation."""

    proposal: PolicyChangeProposal
    """The proposed change or policy to simulate."""


class SimulatePolicyImpactResponse(BaseModel):
    impact: PolicyImpactAssessment
    """AI-generated forecast of the impact of the proposed change."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/simulate-policy-impact", spec=api_spec)
async def run(payload: SimulatePolicyImpactRequest, **kwargs) -> SimulatePolicyImpactResponse:
    """
    Uses behavioral insights and policy context to simulate the likely outcome of a proposed change,
    including risks, opportunities, and advice for successful implementation.
    """
    dummy = PolicyImpactAssessment(
        expected_outcome="The proposed remote work policy is likely to increase satisfaction among developers but may reduce alignment in cross-functional teams.",
        risks=["Possible disconnect between departments", "Reduced informal knowledge sharing"],
        opportunities=["Increased autonomy", "Reduced absenteeism", "Higher retention in tech roles"],
        implementation_advice="Introduce structured check-ins and digital team rituals to compensate for reduced face time."
    )

    return SimulatePolicyImpactResponse(impact=dummy)
