# apis/load_hr_data.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os



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



class LoadHRDataResponse(BaseModel):
    records: List[HRRecord]
    """List of HR records extracted from the source CSV file."""

    total_employees: int
    """Number of unique employees found in the data."""

    total_records: int
    """Total number of HR records loaded from the file."""

    teams_detected: List[str]
    """List of unique team names identified in the data."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "employee_id": "E123",
                            "date": "2024-09-01",
                            "performance_score": 4.2,
                            "absence_days": 1.0,
                            "feedback_text": "Completed tasks consistently, strong communication.",
                            "team": "Marketing"
                        }
                    ],
                    "total_employees": 1,
                    "total_records": 1,
                    "teams_detected": ["Marketing"]
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=False,
)


@prt.api("/load-hr-data", spec=api_spec)
async def run(**kwargs) -> LoadHRDataResponse:
    """Load historical HR data from a fixed CSV path and return normalized HR records for further analysis."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../hr_dataset.csv"))
    df = pd.read_csv(file_path)

    df["team"] = df.get("team", pd.Series(["Unknown"] * len(df)))

    records = [
        HRRecord(
            employee_id=row.get("employee_id", f"UNKNOWN_{i}"),
            date=row.get("date", "1970-01-01"),
            performance_score=row.get("performance_score", None),
            absence_days=row.get("absence_days", 0.0),
            feedback_text=row.get("feedback_text", ""),
            team=row["team"] if isinstance(row, dict) and "team" in row and row["team"] else "Unknown"

        )
        for i, row in df.iterrows()
    ]


    return LoadHRDataResponse(
        records=records,
        total_employees=df["employee_id"].nunique(),
        total_records=len(df),
        teams_detected=df["team"].dropna().unique().tolist()
    )
