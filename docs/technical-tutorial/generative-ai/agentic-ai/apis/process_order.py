# apis/process_order.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class OrderItem(BaseModel):
    item_name: str
    """Name of the item."""

    quantity: int
    """Quantity ordered of the item."""

    unit_price: float
    """Unit price of the item."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"item_name": "Widget", "quantity": 2, "unit_price": 19.99}]},
    }


class ProcessOrderRequest(BaseModel):
    items: List[OrderItem]
    """A list of items in the order."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ]
                }
            ]
        },
    }


class ProcessOrderResponse(BaseModel):
    total: float
    """Total cost of the order."""

    summary: str
    """Summary of the processed order."""

    items: List[OrderItem]
    """The processed list of order items."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "total": 69.97,
                    "summary": "Processed order with 2 items. Total amount: $69.97",
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ],
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/process-order", spec=api_spec)
async def run(payload: ProcessOrderRequest, **kwargs) -> ProcessOrderResponse:
    """Process an order by calculating the total cost and generating a summary."""
    total = sum(item.quantity * item.unit_price for item in payload.items)
    summary = f"Processed order with {len(payload.items)} items. Total amount: ${total:.2f}"
    return ProcessOrderResponse(total=total, summary=summary, items=payload.items)
