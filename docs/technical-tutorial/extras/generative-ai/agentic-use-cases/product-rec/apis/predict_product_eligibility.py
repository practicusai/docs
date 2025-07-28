import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique customer identifier."""

    age: int
    """Age of the customer."""

    gender: str
    """Gender of the customer (e.g., Male, Female)."""

    location: str
    """Customer's region or city."""

    total_purchases: int
    """Number of purchases the customer has made."""

    average_spend: float
    """Average amount the customer spends."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "age": 34,
                    "gender": "Male",
                    "location": "Istanbul",
                    "total_purchases": 12,
                    "average_spend": 84.5
                }
            ]
        }
    }


class PredictEligibilityRequest(BaseModel):
    product_name: str
    """Name of the product to check eligibility for."""

    candidates: List[CustomerProfile]
    """List of customer profiles to check."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_name": "SmartFitness Tracker",
                    "candidates": [
                        {
                            "customer_id": "C019",
                            "age": 34,
                            "gender": "Male",
                            "location": "Istanbul",
                            "total_purchases": 12,
                            "average_spend": 84.5
                        }
                    ]
                }
            ]
        }
    }


class EligibilityPrediction(BaseModel):
    customer_id: str
    """ID of the customer."""

    is_eligible: bool
    """Whether the customer is eligible for the product."""

    reasoning: str
    """Explanation of the eligibility decision."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "is_eligible": True,
                    "reasoning": "Customer has consistent spend above 80 and more than 10 purchases. Good candidate for SmartFitness Tracker."
                }
            ]
        }
    }


class PredictEligibilityResponse(BaseModel):
    results: List[EligibilityPrediction]
    """Eligibility prediction results for each customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "results": [
                        {
                            "customer_id": "C019",
                            "is_eligible": True,
                            "reasoning": "Customer has consistent spend above 80 and more than 10 purchases. Good candidate for SmartFitness Tracker."
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


@prt.api("/predict-product-eligibility", spec=api_spec)
async def run(payload: PredictEligibilityRequest, **kwargs) -> PredictEligibilityResponse:
    """
    Predicts product eligibility for each customer based on profile metrics.
    """

    results = []

    for c in payload.candidates:
        if c.average_spend > 70 and c.total_purchases > 5:
            eligible = True
            reasoning = f"Customer has consistent spend above 70 and more than 5 purchases. Good candidate for {payload.product_name}."
        else:
            eligible = False
            reasoning = f"Customer has insufficient purchase history or low average spend. Not a strong candidate for {payload.product_name}."

        results.append(EligibilityPrediction(
            customer_id=c.customer_id,
            is_eligible=eligible,
            reasoning=reasoning
        ))

    return PredictEligibilityResponse(results=results)
