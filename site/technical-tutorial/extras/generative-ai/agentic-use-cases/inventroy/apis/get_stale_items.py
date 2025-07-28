# apis/get_stale_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime, timedelta


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
                    "product_id": 1088,
                    "product_name": "Peach Juice",
                    "category": "Beverage",
                    "stock_qty": 50,
                    "reorder_threshold": 15,
                    "max_stock": 120,
                    "avg_daily_sales": 0.3,
                    "last_sale_date": "2025-04-15",
                    "expiry_date": "2025-07-10"
                }
            ]
        }
    }


class StaleItemsResponse(BaseModel):
    stale_items: List[InventoryRecord]
    """List of products that have not been sold in the last 30 days."""

    total_stale: int
    """Total number of stale products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "stale_items": [],
                    "total_stale": 0
                }
            ]
        }
    }


class StaleItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for stale items (not sold in the last 30 days)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1088,
                            "product_name": "Peach Juice",
                            "category": "Beverage",
                            "stock_qty": 50,
                            "reorder_threshold": 15,
                            "max_stock": 120,
                            "avg_daily_sales": 0.3,
                            "last_sale_date": "2025-04-15",
                            "expiry_date": "2025-07-10"
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


@prt.api("/get-stale-items", spec=api_spec)
async def run(request: StaleItemsInput, **kwargs) -> StaleItemsResponse:
    """Detect products with no recorded sales in the last 30 days."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["last_sale_date"] = pd.to_datetime(df["last_sale_date"], errors="coerce")

    threshold_date = datetime.utcnow() - timedelta(days=30)
    filtered_df = df[df["last_sale_date"] < threshold_date]

    stale_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return StaleItemsResponse(
        stale_items=stale_items,
        total_stale=len(stale_items)
    )
