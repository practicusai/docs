# apis/get_critical_stock_items.py

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
                    "product_id": 1001,
                    "product_name": "Apple Juice",
                    "category": "Beverage",
                    "stock_qty": 12,
                    "reorder_threshold": 20,
                    "max_stock": 150,
                    "avg_daily_sales": 3.5,
                    "last_sale_date": "2025-06-25",
                    "expiry_date": "2025-07-30"
                }
            ]
        }
    }


class CriticalStockResponse(BaseModel):
    critical_items: List[InventoryRecord]
    """List of items with stock quantity below their reorder threshold."""

    total_critical: int
    """Total number of products found to be understocked."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "critical_items": [],
                    "total_critical": 0
                }
            ]
        }
    }


class CriticalStockInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for critical stock levels."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1001,
                            "product_name": "Apple Juice",
                            "category": "Beverage",
                            "stock_qty": 12,
                            "reorder_threshold": 20,
                            "max_stock": 150,
                            "avg_daily_sales": 3.5,
                            "last_sale_date": "2025-06-25",
                            "expiry_date": "2025-07-30"
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


@prt.api("/get-critical-stock-items", spec=api_spec)
async def run(request: CriticalStockInput, **kwargs) -> CriticalStockResponse:
    """Identify and return products whose stock quantity is below the reorder threshold."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    filtered_df = df[df["stock_qty"] < df["reorder_threshold"]]

    critical_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return CriticalStockResponse(
        critical_items=critical_items,
        total_critical=len(critical_items)
    )
