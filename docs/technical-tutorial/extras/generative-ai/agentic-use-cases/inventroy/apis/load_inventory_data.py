# apis/load_inventory_data.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
import os


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


class LoadInventoryDataResponse(BaseModel):
    records: List[InventoryRecord]
    """List of inventory records extracted from the source CSV file."""

    total_products: int
    """Total number of product entries found in the data."""

    expired_items: int
    """Number of products with expiration date already passed."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [],
                    "total_products": 100,
                    "expired_items": 3
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


@prt.api("/load-inventory-data", spec=api_spec)
async def run(**kwargs) -> LoadInventoryDataResponse:
    """Load inventory data from a fixed CSV path and return structured inventory records."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../inventory_data.csv"))
    df = pd.read_csv(file_path)

    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")
    today = pd.Timestamp.today()

    records = [InventoryRecord(**row) for _, row in df.iterrows()]
    expired_count = df[df["expiry_date"] < today].shape[0]

    return LoadInventoryDataResponse(
        records=records,
        total_products=len(df),
        expired_items=expired_count
    )
