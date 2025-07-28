# apis/calculate_reorder_suggestions.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1201,
                    "product_name": "Mineral Water",
                    "category": "Beverage",
                    "stock_qty": 25,
                    "reorder_threshold": 20,
                    "max_stock": 100,
                    "avg_daily_sales": 1.2,
                    "last_sale_date": "2025-06-25",
                    "expiry_date": "2025-09-01"
                }
            ]
        }
    }


class ReorderSuggestion(BaseModel):
    product_id: int
    """ID of the product suggested for reorder."""

    product_name: str
    """Name of the product."""

    suggested_reorder_qty: int
    """Quantity suggested to reorder."""

    reason: str
    """Reason for the reorder suggestion."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1201,
                    "product_name": "Mineral Water",
                    "suggested_reorder_qty": 30,
                    "reason": "Estimated to fall below reorder threshold within 7 days"
                }
            ]
        }
    }


class ReorderSuggestionsResponse(BaseModel):
    suggestions: List[ReorderSuggestion]
    """List of suggested products to reorder with estimated reorder quantities."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "suggestions": []
                }
            ]
        }
    }


class ReorderSuggestionsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records used to calculate reorder suggestions."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1201,
                            "product_name": "Mineral Water",
                            "category": "Beverage",
                            "stock_qty": 25,
                            "reorder_threshold": 20,
                            "max_stock": 100,
                            "avg_daily_sales": 1.2,
                            "last_sale_date": "2025-06-25",
                            "expiry_date": "2025-09-01"
                        }
                    ]
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


@prt.api("/calculate-reorder-suggestions", spec=api_spec)
async def run(request: ReorderSuggestionsInput, **kwargs) -> ReorderSuggestionsResponse:
    """Suggest products for reorder based on projected 7-day sales and reorder threshold."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["projected_stock"] = df["stock_qty"] - (df["avg_daily_sales"] * 7)

    reorder_df = df[df["projected_stock"] < df["reorder_threshold"]]

    suggestions = []
    for _, row in reorder_df.iterrows():
        suggested_qty = max(int((row["reorder_threshold"] * 1.5) - row["projected_stock"]), 1)
        suggestions.append(ReorderSuggestion(
            product_id=row["product_id"],
            product_name=row["product_name"],
            suggested_reorder_qty=suggested_qty,
            reason="Estimated to fall below reorder threshold within 7 days"
        ))

    return ReorderSuggestionsResponse(suggestions=suggestions)
