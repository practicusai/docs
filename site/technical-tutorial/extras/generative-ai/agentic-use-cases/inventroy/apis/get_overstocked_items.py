# apis/get_overstocked_items.py

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
                    "product_id": 1050,
                    "product_name": "Chocolate",
                    "category": "Snack",
                    "stock_qty": 220,
                    "reorder_threshold": 30,
                    "max_stock": 150,
                    "avg_daily_sales": 1.5,
                    "last_sale_date": "2025-06-22",
                    "expiry_date": "2025-08-01"
                }
            ]
        }
    }


class OverstockedItemsResponse(BaseModel):
    overstocked_items: List[InventoryRecord]
    """List of items with stock quantity above the maximum allowable stock."""

    total_overstocked: int
    """Total number of overstocked products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "overstocked_items": [],
                    "total_overstocked": 0
                }
            ]
        }
    }


class OverstockedItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for overstocked status."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1050,
                            "product_name": "Chocolate",
                            "category": "Snack",
                            "stock_qty": 220,
                            "reorder_threshold": 30,
                            "max_stock": 150,
                            "avg_daily_sales": 1.5,
                            "last_sale_date": "2025-06-22",
                            "expiry_date": "2025-08-01"
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


@prt.api("/get-overstocked-items", spec=api_spec)
async def run(request: OverstockedItemsInput, **kwargs) -> OverstockedItemsResponse:
    """Identify and return products whose stock quantity exceeds their maximum stock limit."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    filtered_df = df[df["stock_qty"] > df["max_stock"]]

    overstocked_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return OverstockedItemsResponse(
        overstocked_items=overstocked_items,
        total_overstocked=len(overstocked_items)
    )
