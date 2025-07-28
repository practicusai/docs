# apis/generate_social_posts.py
import practicuscore as prt
from pydantic import BaseModel


class GenerateSocialPostsRequest(BaseModel):
    campaign_name: str
    """Name of the campaign to generate social posts for"""

    slogan: str
    """Main slogan that will be used across all posts"""

    target_audience: str
    """Short description of who the campaign is targeting"""

    tone: str
    """Tone of voice to be used such as energetic professional or friendly"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "slogan": "Power Up Your Productivity",
                    "target_audience": "Young professionals working remotely in Asia",
                    "tone": "energetic"
                }
            ]
        }
    }


class GenerateSocialPostsResponse(BaseModel):
    linkedin_post: str
    """Generated text post suitable for LinkedIn platform"""

    instagram_caption: str
    """Generated caption designed for Instagram audience"""

    twitter_post: str
    """Generated short post suitable for Twitter or X platform"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "linkedin_post": "Power Up Your Productivity Reach new heights in your remote career with the latest gear",
                    "instagram_caption": "Power meets portability Boost your workflow and elevate your hustle",
                    "twitter_post": "Level up your workspace Power Up Your Productivity"
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-social-posts", spec=api_spec)
async def run(payload: GenerateSocialPostsRequest, **kwargs) -> GenerateSocialPostsResponse:
    """
    Generate platform specific social media posts based on a campaign slogan and audience

    Use this tool after a campaign and slogan are finalized
    Provide the campaign name slogan target audience and tone to receive tailored post texts
    The output includes text formatted for linkedin instagram and twitter
    This tool helps marketing teams save time by creating audience matched content automatically
    """

    slogan = payload.slogan
    audience = payload.target_audience
    tone = payload.tone.lower()

    if "energetic" in tone:
        linkedin = f"{slogan} Reach new heights in your remote career with the latest gear"
        instagram = f"{slogan} Boost your workflow and elevate your hustle"
        twitter = f"Level up your workspace {slogan}"
    elif "professional" in tone:
        linkedin = f"{slogan} A smarter way to work for modern professionals in {audience}"
        instagram = f"{slogan} Designed with professionals in mind"
        twitter = f"{slogan} Professional tools for serious results"
    else:
        linkedin = f"{slogan} Connect with what matters most Perfect for {audience}"
        instagram = f"{slogan} A better day starts with smarter tech"
        twitter = f"{slogan} Ready when you are"

    return GenerateSocialPostsResponse(
        linkedin_post=linkedin,
        instagram_caption=instagram,
        twitter_post=twitter
    )
