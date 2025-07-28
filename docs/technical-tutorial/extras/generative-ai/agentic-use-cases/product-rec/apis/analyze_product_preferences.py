import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict
from collections import Counter


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    past_purchases: List[str]
    """List of product categories previously purchased."""


class AnalyzePreferencesRequest(BaseModel):
    customers: List[CustomerProfile]
    """List of customer profiles including purchase history."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customers": [
                        {
                            "customer_id": "C001",
                            "past_purchases": ["Electronics", "Books", "Electronics"]
                        },
                        {
                            "customer_id": "C002",
                            "past_purchases": ["Beauty", "Books"]
                        }
                    ]
                }
            ]
        }
    }


class PreferenceStats(BaseModel):
    category: str
    """Name of the product category."""

    count: int
    """How many times this category appeared across all customers."""


class AnalyzePreferencesResponse(BaseModel):
    preferences: List[PreferenceStats]
    """Aggregated product preference statistics."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "preferences": [
                        {"category": "Electronics", "count": 2},
                        {"category": "Books", "count": 2},
                        {"category": "Beauty", "count": 1}
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=False,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/analyze-product-preferences", spec=api_spec)
async def run(payload: AnalyzePreferencesRequest, **kwargs) -> AnalyzePreferencesResponse:
    """
    Aggregates past purchase categories to determine overall product preferences
    across the customer base.
    """
    category_counter = Counter()
    for customer in payload.customers:
        category_counter.update(customer.past_purchases)

    results = [
        PreferenceStats(category=cat, count=count)
        for cat, count in category_counter.most_common()
    ]

    return AnalyzePreferencesResponse(preferences=results)
