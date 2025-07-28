# apis/calculate_stock_turnover_rate.py

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
                    "product_id": 1302,
                    "product_name": "Canned Corn",
                    "category": "Grocery",
                    "stock_qty": 150,
                    "reorder_threshold": 30,
                    "max_stock": 200,
                    "avg_daily_sales": 0.5,
                    "last_sale_date": "2025-06-20",
                    "expiry_date": "2026-02-01"
                }
            ]
        }
    }


class TurnoverRecord(BaseModel):
    product_id: int
    """ID of the product."""

    product_name: str
    """Name of the product."""

    turnover_rate: float
    """Calculated turnover rate (avg_daily_sales / stock_qty)."""

    risk_level: str
    """Risk classification based on turnover rate."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1302,
                    "product_name": "Canned Corn",
                    "turnover_rate": 0.0033,
                    "risk_level": "Low"
                }
            ]
        }
    }


class TurnoverRateResponse(BaseModel):
    low_turnover_items: List[TurnoverRecord]
    """List of products with a low stock turnover rate."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "low_turnover_items": []
                }
            ]
        }
    }


class TurnoverRateInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze turnover rates."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1302,
                            "product_name": "Canned Corn",
                            "category": "Grocery",
                            "stock_qty": 150,
                            "reorder_threshold": 30,
                            "max_stock": 200,
                            "avg_daily_sales": 0.5,
                            "last_sale_date": "2025-06-20",
                            "expiry_date": "2026-02-01"
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


@prt.api("/calculate-stock-turnover-rate", spec=api_spec)
async def run(request: TurnoverRateInput, **kwargs) -> TurnoverRateResponse:
    """Calculate stock turnover rate and identify products with low turnover."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["turnover_rate"] = df.apply(
        lambda row: round(row["avg_daily_sales"] / row["stock_qty"], 4) if row["stock_qty"] > 0 else 0.0,
        axis=1
    )

    # Define risk threshold
    low_threshold = 0.02
    low_df = df[df["turnover_rate"] < low_threshold]

    low_turnover_items = [
        TurnoverRecord(
            product_id=row["product_id"],
            product_name=row["product_name"],
            turnover_rate=row["turnover_rate"],
            risk_level="Low"
        )
        for _, row in low_df.iterrows()
    ]

    return TurnoverRateResponse(low_turnover_items=low_turnover_items)
