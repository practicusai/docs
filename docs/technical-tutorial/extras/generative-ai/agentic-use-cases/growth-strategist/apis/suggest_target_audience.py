# apis/suggest_target_audience.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """Name of the campaign"""

    description: str
    """Detailed explanation of the campaign idea"""

    strategy: str
    """Planned marketing strategy for this campaign"""


class SuggestTargetAudienceRequest(BaseModel):
    campaign: GenerateCampaignIdeaResponse
    """The campaign details for which target audience suggestions will be generated"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign": {
                        "campaign_name": "Focus Asia 20",
                        "description": "Boost monitor sales in Asia by promoting productivity.",
                        "strategy": "Use influencer marketing on tech-focused platforms."
                    }
                }
            ]
        }
    }


class AudienceSegment(BaseModel):
    segment_name: str
    """Name of the audience group"""

    age_range: str
    """Typical age range for the audience"""

    profession: str
    """Common job or professional background"""

    interests: List[str]
    """Main interests of this audience segment"""

    persona_summary: str
    """Concise summary describing the lifestyle or preferences of this group"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "segment_name": "Young Remote Workers",
                    "age_range": "25–34",
                    "profession": "Freelancers, Startup Employees",
                    "interests": ["productivity tools", "tech gear", "remote work"],
                    "persona_summary": "Digitally native professionals who value mobility, speed, and high-performance equipment."
                }
            ]
        }
    }


class SuggestTargetAudienceResponse(BaseModel):
    audience_segments: List[AudienceSegment]
    """Suggested audience groups relevant to the campaign"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "audience_segments": [
                        {
                            "segment_name": "Young Remote Workers",
                            "age_range": "25–34",
                            "profession": "Freelancers, Startup Employees",
                            "interests": ["productivity tools", "tech gear", "remote work"],
                            "persona_summary": "Digitally native professionals who value mobility, speed, and high-performance equipment."
                        }
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


@prt.api("/suggest-target-audience", spec=api_spec)
async def run(payload: SuggestTargetAudienceRequest, **kwargs) -> SuggestTargetAudienceResponse:
    """
    Suggest audience segments that are most relevant to a given marketing campaign

    Use this tool when you already have a campaign idea and need to find the most appropriate
    audience groups to target. This helps align the campaign's messaging and channels with
    consumer personas that are most likely to respond.

    The input should include the campaign's name, description, and strategy.
    The output includes one or more audience segments with persona details.
    """

    idea = payload.campaign.description.lower()

    if "remote" in idea or "productivity" in idea:
        segments = [
            AudienceSegment(
                segment_name="Young Remote Workers",
                age_range="25–34",
                profession="Freelancers, Startup Employees",
                interests=["productivity tools", "tech gear", "remote work"],
                persona_summary="Digitally native professionals who value mobility, speed, and high-performance equipment."
            )
        ]
    else:
        segments = [
            AudienceSegment(
                segment_name="General Tech Buyers",
                age_range="30–45",
                profession="Corporate Employees",
                interests=["gadgets", "deals", "online shopping"],
                persona_summary="Professionals with moderate tech interest and stable income, responsive to performance-based messaging."
            )
        ]

    return SuggestTargetAudienceResponse(audience_segments=segments)
