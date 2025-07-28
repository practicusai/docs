import practicuscore as prt
from pydantic import BaseModel
from typing import List


class ProductBundle(BaseModel):
    customer_id: str
    """Unique customer identifier."""

    proposed_bundle: List[str]
    """List of proposed product names in the bundle."""

    past_purchases: List[str]
    """List of past product names the customer has bought."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C022",
                    "proposed_bundle": ["Mouse Pad", "USB-C Hub"],
                    "past_purchases": ["Wireless Mouse", "Laptop Stand"]
                }
            ]
        }
    }


class ScoreBundleAffinityRequest(BaseModel):
    bundles: List[ProductBundle]
    """List of customer bundles to score based on affinity."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "bundles": [
                        {
                            "customer_id": "C022",
                            "proposed_bundle": ["Mouse Pad", "USB-C Hub"],
                            "past_purchases": ["Wireless Mouse", "Laptop Stand"]
                        }
                    ]
                }
            ]
        }
    }


class BundleAffinityScore(BaseModel):
    customer_id: str
    """Customer ID."""

    affinity_score: float
    """Affinity score (0.0 to 1.0) indicating relevance of the product bundle."""

    reason: str
    """Explanation for the score based on overlap or similarity."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C022",
                    "affinity_score": 0.75,
                    "reason": "Partial overlap with prior purchases (Wireless Mouse)."
                }
            ]
        }
    }


class ScoreBundleAffinityResponse(BaseModel):
    scores: List[BundleAffinityScore]
    """List of affinity scores per customer bundle."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "scores": [
                        {
                            "customer_id": "C022",
                            "affinity_score": 0.75,
                            "reason": "Partial overlap with prior purchases (Wireless Mouse)."
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


@prt.api("/score-bundle-affinity", spec=api_spec)
async def run(payload: ScoreBundleAffinityRequest, **kwargs) -> ScoreBundleAffinityResponse:
    """
    Scores the affinity of each proposed product bundle based on the customer's past purchases.
    Higher scores reflect greater similarity or complementarity.
    """
    results = []

    for item in payload.bundles:
        past = set([p.lower() for p in item.past_purchases])
        proposed = set([p.lower() for p in item.proposed_bundle])
        intersection = past.intersection(proposed)

        if not item.past_purchases:
            score = 0.0
            reason = "No past purchases to compare."
        else:
            score = len(intersection) / len(item.proposed_bundle) if item.proposed_bundle else 0.0
            reason = f"{'Partial' if 0 < score < 1 else 'Full' if score == 1 else 'No'} overlap with prior purchases."

        results.append(BundleAffinityScore(
            customer_id=item.customer_id,
            affinity_score=round(score, 2),
            reason=reason
        ))

    return ScoreBundleAffinityResponse(scores=results)
