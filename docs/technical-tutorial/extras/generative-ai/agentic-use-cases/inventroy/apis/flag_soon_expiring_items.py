# apis/flag_soon_expiring_items.py

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
                    "product_id": 1250,
                    "product_name": "Fresh Milk",
                    "category": "Dairy",
                    "stock_qty": 60,
                    "reorder_threshold": 25,
                    "max_stock": 120,
                    "avg_daily_sales": 3.0,
                    "last_sale_date": "2025-06-24",
                    "expiry_date": "2025-07-05"
                }
            ]
        }
    }


class SoonExpiringItemsResponse(BaseModel):
    soon_expiring_items: List[InventoryRecord]
    """List of items that will expire within the next 14 days."""

    total_soon_expiring: int
    """Total number of soon-to-expire products."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "soon_expiring_items": [],
                    "total_soon_expiring": 0
                }
            ]
        }
    }


class SoonExpiringItemsInput(BaseModel):
    records: List[InventoryRecord]
    """List of inventory items to evaluate for upcoming expiration."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1250,
                            "product_name": "Fresh Milk",
                            "category": "Dairy",
                            "stock_qty": 60,
                            "reorder_threshold": 25,
                            "max_stock": 120,
                            "avg_daily_sales": 3.0,
                            "last_sale_date": "2025-06-24",
                            "expiry_date": "2025-07-05"
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


@prt.api("/flag-soon-expiring-items", spec=api_spec)
async def run(request: SoonExpiringItemsInput, **kwargs) -> SoonExpiringItemsResponse:
    """Identify products that are due to expire within the next 14 days."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    deadline = datetime.utcnow() + timedelta(days=14)
    filtered_df = df[(df["expiry_date"] >= datetime.utcnow()) & (df["expiry_date"] <= deadline)]

    soon_expiring_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return SoonExpiringItemsResponse(
        soon_expiring_items=soon_expiring_items,
        total_soon_expiring=len(soon_expiring_items)
    )
