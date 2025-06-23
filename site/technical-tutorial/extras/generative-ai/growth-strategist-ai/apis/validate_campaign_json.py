# apis/validate_campaign_json.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class CampaignData(BaseModel):
    campaign_name: str
    """Name of the campaign to be validated"""

    description: str
    """Detailed description of the campaign’s objective and context"""

    strategy: str
    """High-level marketing strategy or approach"""

    slogans: List[str]
    """List of proposed slogans that support the campaign"""

    audience_segments: List[str]
    """Target customer segments the campaign is intended for"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "description": "Boost monitor sales in Asia with productivity-focused messaging.",
                    "strategy": "Use influencers on social media platforms and offer bundle promotions.",
                    "slogans": ["Power Up Your Productivity!", "See More, Do More."],
                    "audience_segments": ["Young Remote Workers", "Tech-Savvy Freelancers"]
                }
            ]
        }
    }


class ValidateCampaignJSONResponse(BaseModel):
    is_valid: bool
    """Indicates if the campaign JSON object is structurally complete"""

    missing_fields: List[str]
    """Names of fields that are missing or empty"""

    message: str
    """Explanation message summarizing the validation result"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "is_valid": False,
                    "missing_fields": ["strategy"],
                    "message": "Missing required field(s): strategy."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/validate-campaign-json", spec=api_spec)
async def run(payload: CampaignData, **kwargs) -> ValidateCampaignJSONResponse:
    """
    Validate if a campaign object is complete and ready to be used in downstream tools

    This tool checks the internal structure of a campaign definition to ensure that
    all required fields are present and non-empty.

    Use this tool when:
    - You receive a campaign JSON from another tool or agent
    - You want to ensure no critical data (like name, strategy, or slogans) is missing
    - You want to fail-fast before further processing a campaign

    Input: Campaign object with fields like name, description, strategy, slogans, and audience
    Output: A boolean indicating if the campaign is valid and which fields are missing if any
    """

    missing = []

    if not payload.campaign_name.strip():
        missing.append("campaign_name")
    if not payload.description.strip():
        missing.append("description")
    if not payload.strategy.strip():
        missing.append("strategy")
    if not payload.slogans or all(not s.strip() for s in payload.slogans):
        missing.append("slogans")
    if not payload.audience_segments:
        missing.append("audience_segments")

    is_valid = len(missing) == 0
    message = "All required fields are present." if is_valid else f"Missing required field(s): {', '.join(missing)}."

    return ValidateCampaignJSONResponse(
        is_valid=is_valid,
        missing_fields=missing,
        message=message
    )
