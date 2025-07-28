import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict


class PurchaseHistory(BaseModel):
    customer_id: str
    """Unique customer ID."""

    previous_products: List[str]
    """List of previously purchased product names."""

    total_spend: float
    """Total amount spent by the customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "previous_products": ["Wireless Mouse", "Laptop Stand", "Keyboard"],
                    "total_spend": 320.5
                }
            ]
        }
    }


class SuggestBundleRequest(BaseModel):
    histories: List[PurchaseHistory]
    """List of customer purchase histories."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "histories": [
                        {
                            "customer_id": "C019",
                            "previous_products": ["Wireless Mouse", "Laptop Stand", "Keyboard"],
                            "total_spend": 320.5
                        }
                    ]
                }
            ]
        }
    }


class BundleSuggestion(BaseModel):
    customer_id: str
    """Customer ID."""

    recommended_bundle: List[str]
    """List of suggested products as a dynamic bundle."""

    reason: str
    """Reason for suggesting this bundle."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "recommended_bundle": ["Bluetooth Headphones", "USB Hub"],
                    "reason": "Customer previously purchased work-from-home accessories. Recommended complementary items."
                }
            ]
        }
    }


class SuggestBundleResponse(BaseModel):
    suggestions: List[BundleSuggestion]
    """List of dynamic product bundle suggestions per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "suggestions": [
                        {
                            "customer_id": "C019",
                            "recommended_bundle": ["Bluetooth Headphones", "USB Hub"],
                            "reason": "Customer previously purchased work-from-home accessories. Recommended complementary items."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Medium
)


@prt.api("/suggest-dynamic-product-bundle", spec=api_spec)
async def run(payload: SuggestBundleRequest, **kwargs) -> SuggestBundleResponse:
    """
    Suggests product bundles dynamically based on customer purchase history.
    """

    bundle_db = {
        "Laptop Stand": ["USB-C Hub", "Laptop Sleeve"],
        "Wireless Mouse": ["Mouse Pad", "Keyboard"],
        "Keyboard": ["Wrist Rest", "Monitor Riser"],
        "Smartphone Case": ["Screen Protector", "Phone Grip"],
        "Yoga Mat": ["Resistance Bands", "Foam Roller"]
    }

    suggestions = []

    for h in payload.histories:
        recommended = []
        reasons = []

        for item in h.previous_products:
            if item in bundle_db:
                recommended.extend(bundle_db[item])
                reasons.append(f"Related to previous purchase: {item}")

        unique_recommended = list(set(recommended))
        reason_text = " | ".join(reasons) if reasons else "Based on previous purchase categories."

        suggestions.append(BundleSuggestion(
            customer_id=h.customer_id,
            recommended_bundle=unique_recommended,
            reason=reason_text
        ))

    return SuggestBundleResponse(suggestions=suggestions)
