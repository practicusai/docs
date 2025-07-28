# apis/get_expired_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime


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
                    "product_id": 1100,
                    "product_name": "Yogurt",
                    "category": "Dairy",
                    "stock_qty": 40,
                    "reorder_threshold": 20,
                    "max_stock": 100,
                    "avg_daily_sales": 2.2,
                    "last_sale_date": "2025-06-24",
                    "expiry_date": "2025-06-15"
                }
            ]
        }
    }


class ExpiredItemsResponse(BaseModel):
    expired_items: List[InventoryRecord]
    """List of products whose expiration date has already passed."""

    total_expired: int
    """Total number of expired products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "expired_items": [],
                    "total_expired": 0
                }
            ]
        }
    }


class ExpiredItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for expiration status."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1100,
                            "product_name": "Yogurt",
                            "category": "Dairy",
                            "stock_qty": 40,
                            "reorder_threshold": 20,
                            "max_stock": 100,
                            "avg_daily_sales": 2.2,
                            "last_sale_date": "2025-06-24",
                            "expiry_date": "2025-06-15"
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


@prt.api("/get-expired-items", spec=api_spec)
async def run(request: ExpiredItemsInput, **kwargs) -> ExpiredItemsResponse:
    """Detect expired products based on their expiration date."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    today = datetime.utcnow()
    expired_df = df[df["expiry_date"] < today]

    expired_items = [InventoryRecord(**row) for _, row in expired_df.iterrows()]

    return ExpiredItemsResponse(
        expired_items=expired_items,
        total_expired=len(expired_items)
    )
