# apis/detect_regional_drop.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from collections import defaultdict


class SalesRecord(BaseModel):
    date: datetime
    """The UTC date when the sale was recorded."""

    product: str
    """The name of the product sold."""

    region: str
    """The geographical region where the product was sold."""

    units_sold: int
    """The number of units sold in this transaction."""

    revenue: float
    """The total revenue generated from the sale."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Monitor",
                    "region": "Asia",
                    "units_sold": 150,
                    "revenue": 45000.0
                }
            ]
        }
    }


class DetectRegionalDropRequest(BaseModel):
    sales_data: List[SalesRecord]
    """List of sales transactions to analyze."""

    start_date: datetime
    """Start date of the analysis window (UTC)."""

    end_date: datetime
    """End date of the analysis window (UTC)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Monitor",
                            "region": "Asia",
                            "units_sold": 150,
                            "revenue": 45000.0
                        }
                    ],
                    "start_date": "2024-12-01T00:00:00Z",
                    "end_date": "2025-02-28T00:00:00Z"
                }
            ]
        }
    }


class RegionalDrop(BaseModel):
    region: str
    """Region where the sales drop was detected."""

    product: str
    """Product that showed a decrease in sales."""

    drop_percentage: float
    """Percentage of decline in units sold between the two periods."""

    comment: Optional[str]
    """Optional explanation or context about the decline."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "region": "Asia",
                    "product": "Monitor",
                    "drop_percentage": 42.5,
                    "comment": "Sales declined sharply compared to the previous period."
                }
            ]
        }
    }


class DetectRegionalDropResponse(BaseModel):
    drops: List[RegionalDrop]
    """List of regional product drops with percentage and commentary."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "drops": [
                        {
                            "region": "Asia",
                            "product": "Monitor",
                            "drop_percentage": 42.5,
                            "comment": "Sales declined sharply compared to the previous period."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)



@prt.api("/detect-regional-drop", spec=api_spec)
async def run(payload: DetectRegionalDropRequest, **kwargs) -> DetectRegionalDropResponse:
    """
    Detect regional drops in product sales over a selected date range.
    Compares first and second half of the period to find significant declines.
    """
    try:
        
        from datetime import timezone

        def make_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)


        start_date = make_utc(payload.start_date)
        end_date = make_utc(payload.end_date)
        mid_point = start_date + (end_date - start_date) / 2

        current_period = defaultdict(list)
        previous_period = defaultdict(list)

        for r in payload.sales_data:
            r_date = make_utc(r.date)
            if start_date <= r_date <= mid_point:
                previous_period[(r.region, r.product)].append(r.units_sold)
            elif mid_point < r_date <= end_date:
                current_period[(r.region, r.product)].append(r.units_sold)

        drops = []
        for key in previous_period:
            prev_avg = sum(previous_period[key]) / len(previous_period[key]) if previous_period[key] else 0
            curr_avg = sum(current_period.get(key, [])) / len(current_period.get(key, [])) if current_period.get(key) else 0

            if prev_avg > 0 and curr_avg < prev_avg * 0.85:
                drop_pct = round((prev_avg - curr_avg) / prev_avg * 100, 2)
                drops.append(RegionalDrop(
                    region=key[0],
                    product=key[1],
                    drop_percentage=drop_pct,
                    comment="Sales declined sharply compared to the previous period."
                ))

        return DetectRegionalDropResponse(drops=drops)

    except Exception as e:
        prt.logger.error(f"[detect-regional-drop] Exception: {e}")
        raise
