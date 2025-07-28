# apis/summarize_stock_health.py

import practicuscore as prt
from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    critical_count: int = Field(..., description="Number of products with stock below reorder threshold")
    overstocked_count: int = Field(..., description="Number of products with stock above max limit")
    stale_count: int = Field(..., description="Number of products with no sales in the last 30 days")
    expired_count: int = Field(..., description="Number of expired products")

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "critical_count": 3,
                    "overstocked_count": 5,
                    "stale_count": 2,
                    "expired_count": 1
                }
            ]
        }
    }


class StockHealthSummary(BaseModel):
    summary: str
    """A natural language summary describing the current stock health situation."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "There are 3 critical items requiring immediate restock. 5 products are overstocked, suggesting excess inventory. 2 products have had no sales in the last 30 days. 1 product is expired and must be removed from stock."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/summarize-stock-health", spec=api_spec)
async def run(request: SummaryRequest) -> StockHealthSummary:
    """Generate a summary statement based on the given inventory analysis counts."""
    parts = []

    if request.critical_count > 0:
        parts.append(f"{request.critical_count} critical item(s) require immediate restocking")
    if request.overstocked_count > 0:
        parts.append(f"{request.overstocked_count} item(s) are overstocked and may need clearance")
    if request.stale_count > 0:
        parts.append(f"{request.stale_count} item(s) have had no sales in the last 30 days")
    if request.expired_count > 0:
        parts.append(f"{request.expired_count} expired item(s) must be removed from inventory")

    if not parts:
        summary = "Inventory levels are healthy. No critical issues detected."
    else:
        summary = ". ".join(parts) + "."

    return StockHealthSummary(summary=summary)
