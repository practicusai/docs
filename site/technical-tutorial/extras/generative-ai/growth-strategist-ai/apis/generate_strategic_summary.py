# apis/generate_strategic_summary.py

import practicuscore as prt
from pydantic import BaseModel


class CampaignIdea(BaseModel):
    campaign_name: str
    """The name of the campaign."""

    description: str
    """A brief explanation of the campaign."""

    strategy: str
    """The strategy to be used in the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Monitor Boost in Asia",
                    "description": "This campaign focuses on growing Monitor sales in Asia, supporting the goal: 'Increase monitor sales in Asia by 20% in Q2.'",
                    "strategy": "Leverage digital ads and local influencers in Asia. Highlight features that align with productivity and affordability."
                }
            ]
        }
    }


class StrategicSummaryResponse(BaseModel):
    summary: str
    """A concise strategic overview of the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "The campaign targets a high-growth region using localized advertising and product positioning to emphasize productivity gains."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-strategic-summary", spec=api_spec)
async def run(payload: CampaignIdea, **kwargs) -> StrategicSummaryResponse:
    """
    This tool generates a short strategic summary from a campaign idea
    It is used when a decision maker wants a quick strategic overview of a campaign's purpose and method
    Input includes campaign name, description, and strategy
    Output includes a synthesized sentence summarizing the strategic intent
    Useful for briefings and high-level analysis
    """

    summary = f"The campaign '{payload.campaign_name}' aims to achieve its business goal by {payload.strategy.lower()}. It is designed to address the objective: {payload.description}"
    return StrategicSummaryResponse(summary=summary)
