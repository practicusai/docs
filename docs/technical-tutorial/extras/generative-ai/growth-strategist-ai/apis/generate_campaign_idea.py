# apis/generate_campaign_idea.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GrowthOpportunity(BaseModel):
    product: str
    """The product that represents a growth opportunity."""

    region: str
    """The region where this product shows growth potential."""

    reason: str
    """Explanation of why this product-region combination is promising."""

    confidence: str
    """Confidence level of the opportunity (e.g., high, medium, low)."""


class GenerateCampaignIdeaRequest(BaseModel):
    goal: str
    """The business goal in natural language (e.g., increase monitor sales in Asia by 20%)."""

    opportunities: List[GrowthOpportunity]
    """A list of previously identified product-region growth opportunities."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "goal": "Increase monitor sales in Asia by 20% in Q1",
                    "opportunities": [
                        {
                            "product": "Monitor",
                            "region": "Asia",
                            "reason": "Strong market potential with recent positive sales trend.",
                            "confidence": "high"
                        }
                    ]
                }
            ]
        }
    }


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """A short and catchy name for the proposed marketing campaign."""

    description: str
    """A one-paragraph summary of what the campaign aims to achieve."""

    strategy: str
    """A suggested strategic approach to achieve the campaign's goal."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "description": "A regional campaign to boost monitor sales by highlighting productivity and affordability.",
                    "strategy": "Use targeted ads on professional networks and bundled discounts for remote workers."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-campaign-idea", spec=api_spec)
async def run(payload: GenerateCampaignIdeaRequest, **kwargs) -> GenerateCampaignIdeaResponse:
    """
    Generate a marketing campaign plan based on a defined business goal and a list of growth opportunities.

    Use this tool when a user provides a clear objective and market insights,
    and needs help forming a compelling campaign concept.

    The input includes a business goal and opportunity details (product, region, reason, confidence).
    The output includes a campaign name, high-level description, and suggested strategy.
    This tool supports decision-making for sales and marketing initiatives.
    """

    goal = payload.goal
    product_names = [op.product for op in payload.opportunities]
    region_names = [op.region for op in payload.opportunities]

    campaign_name = f"{product_names[0]} Boost in {region_names[0]}"
    description = f"This campaign focuses on growing {product_names[0]} sales in {region_names[0]}, supporting the goal: '{goal}'."
    strategy = f"Leverage digital ads and local influencers in {region_names[0]}. Highlight features that align with productivity and affordability."

    return GenerateCampaignIdeaResponse(
        campaign_name=campaign_name,
        description=description,
        strategy=strategy
    )
