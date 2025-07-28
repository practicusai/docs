# apis/detect_behavior_flags.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class HRRecord(BaseModel):
    employee_id: str
    """Employee identifier."""

    date: str
    """Record date (format: YYYY-MM-DD)."""

    performance_score: Optional[float]
    """Score representing employee's performance."""

    absence_days: Optional[float]
    """Number of days the employee was absent."""

    feedback_text: Optional[str]
    """Feedback comment or remark."""

    team: Optional[str]
    """Team name; if not provided, will be defaulted."""


class BehaviorFlag(BaseModel):
    employee_id: str
    """Employee for whom the flag was detected."""

    absence_flag: bool
    """True if absence_days > 5."""

    performance_flag: bool
    """True if performance_score < 2.5."""

    team: str
    """Normalized team name for grouping."""


class DetectBehaviorFlagsRequest(BaseModel):
    records: List[HRRecord]
    """List of HR records to evaluate."""


class DetectBehaviorFlagsResponse(BaseModel):
    flags: List[BehaviorFlag]
    """Flags for each employee indicating behavioral signals."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/detect-behavior-flags", spec=api_spec)
async def run(payload: DetectBehaviorFlagsRequest) -> DetectBehaviorFlagsResponse:
    """Detect simple behavioral flags like high absence or low performance."""
    flags = []

    for r in payload.records:
        absence_flag = (r.absence_days or 0) > 5
        performance_flag = (r.performance_score or 5) < 2.5
        team = r.team if r.team else "Unknown"

        flags.append(BehaviorFlag(
            employee_id=r.employee_id,
            absence_flag=absence_flag,
            performance_flag=performance_flag,
            team=team
        ))

    return DetectBehaviorFlagsResponse(flags=flags)
