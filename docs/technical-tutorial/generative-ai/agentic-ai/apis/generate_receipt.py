# apis/generate_receipt.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List
from datetime import datetime


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


class GenerateReceiptRequest(BaseModel):
    summary: str
    """Order summary from the processed order."""

    total: float
    """Total cost of the order."""

    items: List[OrderItem]
    """List of order items."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Processed order with 2 items. Total amount: $69.97",
                    "total": 69.97,
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ],
                }
            ]
        },
    }


class GenerateReceiptResponse(BaseModel):
    receipt: str
    """The formatted receipt."""

    timestamp: str
    """Timestamp when the receipt was generated."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "receipt": (
                        "----- RECEIPT -----\n"
                        "Processed order with 2 items. Total amount: $69.97\n"
                        "Items:\n"
                        "Widget: 2 x $19.99 = $39.98\n"
                        "Gadget: 1 x $29.99 = $29.99\n"
                        "Total: $69.97\n"
                        "-------------------"
                    ),
                    "timestamp": "2023-01-01T00:00:00Z",
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-receipt", spec=api_spec)
async def run(payload: GenerateReceiptRequest, **kwargs) -> GenerateReceiptResponse:
    """Generate a formatted receipt from the processed order data."""
    receipt_lines = ["----- RECEIPT -----", payload.summary, "Items:"]
    for item in payload.items:
        line = f"{item.item_name}: {item.quantity} x ${item.unit_price:.2f} = ${item.quantity * item.unit_price:.2f}"
        receipt_lines.append(line)
    receipt_lines.append(f"Total: ${payload.total:.2f}")
    receipt_lines.append("-------------------")
    receipt_text = "\n".join(receipt_lines)
    timestamp = datetime.utcnow().isoformat() + "Z"
    return GenerateReceiptResponse(receipt=receipt_text, timestamp=timestamp)
