# apis/analyze_sales_trends.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime, timezone


class SalesTrendSummary(BaseModel):
    trend_direction: Literal["increasing", "decreasing", "stable"]
    """Overall direction of sales trend"""

    peak_day: str
    """Day with the highest sales, in YYYY-MM-DD format"""


class SalesRecord(BaseModel):
    date: datetime
    """The date of the sales transaction in UTC format."""

    product: str
    """The name of the product sold."""

    region: str
    """The geographical region where the sale occurred."""

    units_sold: int
    """The number of product units sold."""

    revenue: float
    """The total revenue generated from this sale."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Laptop",
                    "region": "Asia",
                    "units_sold": 120,
                    "revenue": 120000.0
                }
            ]
        }
    }


class AnalyzeSalesTrendsRequest(BaseModel):
    sales_data: List[SalesRecord]
    """List of sales records to analyze."""

    start_date: datetime
    """The start date of the period to be analyzed, in UTC."""

    end_date: datetime
    """The end date of the period to be analyzed, in UTC."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Laptop",
                            "region": "Asia",
                            "units_sold": 120,
                            "revenue": 120000.0
                        }
                    ],
                    "start_date": "2024-12-01T00:00:00Z",
                    "end_date": "2024-12-31T00:00:00Z"
                }
            ]
        }
    }


class AnalyzeSalesTrendsResponse(BaseModel):
    total_units: int
    """Total number of units sold in the analyzed period."""

    total_revenue: float
    """Total revenue generated in the analyzed period."""

    daily_average_units: float
    """Average number of units sold per day."""

    trend_summary: SalesTrendSummary
    """Summary of trend direction and peak day."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "total_units": 30500,
                    "total_revenue": 15200000.0,
                    "daily_average_units": 492.06,
                    "trend_summary": {
                        "trend_direction": "increasing",
                        "peak_day": "2025-01-10"
                    }
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/analyze-sales-trends", spec=api_spec)
async def run(payload: AnalyzeSalesTrendsRequest, **kwargs) -> AnalyzeSalesTrendsResponse:
    """
    Analyze overall sales performance for a selected date range V19.
    Provides total units sold, revenue, daily averages, trend direction and peak day.
    """

    try:
        def make_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        start_date = make_utc(payload.start_date)
        end_date = make_utc(payload.end_date)

        filtered = [
            record for record in payload.sales_data
            if start_date <= make_utc(record.date) <= end_date
        ]

        if not filtered:
            return AnalyzeSalesTrendsResponse(
                total_units=0,
                total_revenue=0.0,
                daily_average_units=0.0,
                trend_summary=SalesTrendSummary(
                    trend_direction="stable",
                    peak_day="N/A"
                )
            )

        filtered.sort(key=lambda x: x.date)

        total_units = sum(r.units_sold for r in filtered)
        total_revenue = sum(r.revenue for r in filtered)
        num_days = (end_date - start_date).days + 1
        daily_avg = total_units / num_days if num_days else 0

        first_avg = sum(r.units_sold for r in filtered[:5]) / 5
        last_avg = sum(r.units_sold for r in filtered[-5:]) / 5

        if last_avg > first_avg * 1.1:
            trend = "increasing"
        elif last_avg < first_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        day_totals = {}
        for r in filtered:
            dt = make_utc(r.date)
            day_totals.setdefault(dt, 0)
            day_totals[dt] += r.units_sold
        peak_day = max(day_totals, key=day_totals.get).strftime("%Y-%m-%d")

        return AnalyzeSalesTrendsResponse(
            total_units=total_units,
            total_revenue=total_revenue,
            daily_average_units=round(daily_avg, 2),
            trend_summary={
                "trend_direction": trend,
                "peak_day": peak_day
            }
        )

    except Exception as e:
        prt.logger.error(f"[analyze-sales-trends] Exception: {e}")
        raise
