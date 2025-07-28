# apis/analyze_engagement_trend.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class HRRecord(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    date: str
    """Timestamp of the HR record."""

    performance_score: float
    """Performance score at that time."""

    absence_days: float
    """Number of absence days within the period."""

    feedback_text: str
    """Free-form feedback or comment received."""


class EngagementTrend(BaseModel):
    employee_id: str
    """Employee for whom the trend is analyzed."""

    trend_direction: str
    """Direction of engagement trend: 'Improving', 'Declining', or 'Stable'."""

    insight: str
    """LLM-generated explanation of why this trend was detected."""

    intervention_needed: bool
    """Whether action should be taken based on this trend."""


class AnalyzeEngagementTrendRequest(BaseModel):
    records: List[HRRecord]
    """Historical HR records used to detect engagement trend."""


class AnalyzeEngagementTrendResponse(BaseModel):
    trends: List[EngagementTrend]
    """Trend evaluations per employee."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/analyze-engagement-trend", spec=api_spec)
async def run(payload: AnalyzeEngagementTrendRequest, **kwargs) -> AnalyzeEngagementTrendResponse:
    """
    Analyzes historical engagement signals to detect trends in employee behavior over time,
    highlighting if intervention may be required.
    """
    dummy = EngagementTrend(
        employee_id=payload.records[0].employee_id,
        trend_direction="Declining",
        insight="Performance scores are dropping steadily while absenteeism is increasing. Feedback mentions loss of motivation.",
        intervention_needed=True
    )

    return AnalyzeEngagementTrendResponse(trends=[dummy])
