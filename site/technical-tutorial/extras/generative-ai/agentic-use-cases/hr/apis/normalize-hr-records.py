import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional



class HRRecord(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    date: str
    """Date of the HR record (format: YYYY-MM-DD)."""

    performance_score: Optional[float] = None
    """Performance score assigned to the employee."""

    absence_days: Optional[float] = None
    """Number of absence days recorded."""

    feedback_text: Optional[str] = None
    """Free-text feedback or comment regarding the employee."""

    team: Optional[str] = None
    """Team or department the employee belongs to."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "employee_id": "E123",
                    "date": "2024-09-01",
                    "performance_score": 4.2,
                    "absence_days": 1.0,
                    "feedback_text": "Completed tasks consistently, strong communication.",
                    "team": "Marketing"
                }
            ]
        },
    }


class NormalizeHRRecordsResponse(BaseModel):
    normalized_records: List[HRRecord]
    """List of cleaned and normalized HR records."""

    message: str
    """Message indicating status or transformation result."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "normalized_records": [
                        {
                            "employee_id": "E123",
                            "date": "2024-09-01",
                            "performance_score": 4.2,
                            "absence_days": 1.0,
                            "feedback_text": "Completed tasks consistently, strong communication.",
                            "team": "Marketing"
                        }
                    ],
                    "message": "Normalized 1 HR records."
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=False,
)


@prt.api("/normalize-hr-records", spec=api_spec)
async def run(records: List[HRRecord]) -> NormalizeHRRecordsResponse:
    """Normalize raw HR records to ensure all fields are complete and standardized."""

    if not records:
        dummy = HRRecord(
            employee_id="DUMMY",
            date="2024-01-01",
            performance_score=3.0,
            absence_days=0.0,
            feedback_text="Placeholder feedback.",
            team="Unknown"
        )
        return NormalizeHRRecordsResponse(
            normalized_records=[dummy],
            message="Input was empty. Injected dummy HR record for simulation."
        )

    normalized = []
    for rec in records:
        normalized.append(
            HRRecord(
                employee_id=rec.employee_id,
                date=rec.date,
                performance_score=rec.performance_score if rec.performance_score is not None else 0.0,
                absence_days=rec.absence_days if rec.absence_days is not None else 0.0,
                feedback_text=rec.feedback_text or "No feedback provided.",
                team=rec.team or "Unknown"
            )
        )

    return NormalizeHRRecordsResponse(
        normalized_records=normalized,
        message=f"Normalized {len(normalized)} HR records."
    )
