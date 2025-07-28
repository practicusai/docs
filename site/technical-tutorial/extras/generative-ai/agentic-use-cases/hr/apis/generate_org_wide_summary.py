# apis/generate_org_wide_summary.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class TeamSummary(BaseModel):
    team_name: str
    """Name of the team."""

    health_summary: str
    """Brief summary of team-level observations."""

    risk_distribution: str
    """Burnout risk breakdown."""

    key_recommendation: str
    """Team-level managerial suggestion."""


class OrgWideInsight(BaseModel):
    executive_summary: str
    """One-paragraph strategic summary of the entire workforce health and trends."""

    common_risks: List[str]
    """List of shared concerns across multiple departments."""

    org_opportunities: List[str]
    """Emerging strengths or organizational leverage points."""

    strategic_recommendation: str
    """High-level leadership recommendation (e.g. cultural shift, structure, resourcing)."""


class GenerateOrgWideSummaryRequest(BaseModel):
    team_summaries: List[TeamSummary]
    """Aggregated team summaries to be used for org-wide analysis."""


class GenerateOrgWideSummaryResponse(BaseModel):
    org_summary: OrgWideInsight
    """Strategic summary and insight generation for executive review."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-org-wide-summary", spec=api_spec)
async def run(payload: GenerateOrgWideSummaryRequest, **kwargs) -> GenerateOrgWideSummaryResponse:
    """
    Generates a high-level strategic summary across all teams,
    identifying cross-cutting risks, opportunities, and recommendations for leadership.
    """
    dummy = OrgWideInsight(
        executive_summary="Across all departments, there is a growing risk of burnout and disengagement in mid-level roles, while technical teams show resilience.",
        common_risks=["Mid-level manager fatigue", "Disconnect between hybrid teams", "Unclear career paths"],
        org_opportunities=["Strong peer mentoring culture in R&D", "Improved onboarding process in Sales"],
        strategic_recommendation="Initiate leadership upskilling, review role clarity in mid-management, and expand peer mentoring across units."
    )

    return GenerateOrgWideSummaryResponse(org_summary=dummy)
