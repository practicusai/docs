# apis/generate_marketing_slogan.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """Name of the campaign being promoted."""

    description: str
    """Detailed description explaining the campaign purpose."""

    strategy: str
    """Suggested strategy to execute the campaign."""


class GenerateMarketingSloganRequest(BaseModel):
    campaign: GenerateCampaignIdeaResponse
    """Full campaign details (name, description, and strategy) used to generate slogans."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign": {
                        "campaign_name": "Focus Asia 20",
                        "description": "A regional campaign to boost monitor sales by highlighting productivity.",
                        "strategy": "Leverage social media influencers and promote bundled deals."
                    }
                }
            ]
        }
    }


class GenerateMarketingSloganResponse(BaseModel):
    slogans: List[str]
    """List of suggested marketing slogans tailored to the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "slogans": [
                        "Power Up Your Productivity!",
                        "The Monitor That Works As Hard As You Do.",
                        "Boost Your Vision, Boost Your Goals."
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-marketing-slogan", spec=api_spec)
async def run(payload: GenerateMarketingSloganRequest, **kwargs) -> GenerateMarketingSloganResponse:
    """
    Generate catchy marketing slogans from a campaign description and strategy.

    Use this tool when a campaign is already defined and you need creative slogan ideas.
    The input must contain a structured campaign object including name, description, and strategy.
    The output is a list of short slogans designed to align with the campaign tone and goal.

    Ideal for marketing teams looking to quickly brainstorm branding lines.
    """

    description = payload.campaign.description.lower()

    if "productivity" in description:
        slogans = [
            "Power Up Your Productivity!",
            "Work Smarter, See Sharper.",
            "Boost Your Workflow with Every Pixel."
        ]
    elif "deal" in description:
        slogans = [
            "Big Value, Bigger Vision.",
            "Bundles That Mean Business.",
            "Smart Tech. Smarter Price."
        ]
    else:
        slogans = [
            "Your Tech, Your Edge.",
            "Be Bold. Be Better.",
            "Innovation in Every Click."
        ]

    return GenerateMarketingSloganResponse(slogans=slogans)
