# apis/send_confirmation.py
import practicuscore as prt
from pydantic import BaseModel


class SendConfirmationRequest(BaseModel):
    receipt: str
    """The receipt text to be used in the confirmation message."""

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
                    )
                }
            ]
        },
    }


class SendConfirmationResponse(BaseModel):
    confirmation_message: str
    """The confirmation message including the receipt."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "confirmation_message": (
                        "Order confirmed! Here is your receipt:\n"
                        "----- RECEIPT -----\n"
                        "Processed order with 2 items. Total amount: $69.97\n"
                        "Items:\n"
                        "Widget: 2 x $19.99 = $39.98\n"
                        "Gadget: 1 x $29.99 = $29.99\n"
                        "Total: $69.97\n"
                        "-------------------"
                    )
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.High,
    idempotent=False,
    human_gated=True,
)


@prt.api("/send-confirmation", spec=api_spec)
async def run(payload: SendConfirmationRequest, **kwargs) -> SendConfirmationResponse:
    """Send an order confirmation message based on the provided receipt."""
    confirmation_message = f"Order confirmed! Here is your receipt:\n{payload.receipt}"
    return SendConfirmationResponse(confirmation_message=confirmation_message)
