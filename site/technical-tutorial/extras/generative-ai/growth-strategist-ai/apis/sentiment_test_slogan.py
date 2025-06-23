# apis/sentiment_test_slogan.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Literal
from langchain_openai import ChatOpenAI


class SentimentTestSloganRequest(BaseModel):
    slogans: List[str]
    """List of slogans to analyze for emotional sentiment"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{
                "slogans": [
                    "Power Up Your Productivity!",
                    "You Deserve Better."
                ]
            }]
        }
    }


class SloganSentimentResult(BaseModel):
    slogan: str
    """The original marketing slogan"""

    sentiment: Literal["positive", "neutral", "negative"]
    """Detected emotional sentiment of the slogan"""

    comment: str
    """Short explanation of the sentiment classification"""


class SentimentTestSloganResponse(BaseModel):
    results: List[SloganSentimentResult]
    """Sentiment results for each input slogan"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{
                "results": [
                    {
                        "slogan": "Power Up Your Productivity!",
                        "sentiment": "positive",
                        "comment": "This slogan conveys a sense of motivation and improvement."
                    },
                    {
                        "slogan": "You Deserve Better.",
                        "sentiment": "neutral",
                        "comment": "This slogan implies improvement but lacks strong emotional cues."
                    }
                ]
            }]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/sentiment-test-slogan", spec=api_spec)
async def run(payload: SentimentTestSloganRequest, **kwargs) -> SentimentTestSloganResponse:
    """
    Analyze the emotional sentiment of given marketing slogans using a language model

    Use this tool when you have one or more slogans and want to understand the
    emotional tone behind each one. The output helps determine if a slogan
    is likely to be received as positive, neutral, or negative.

    Useful for validating slogans before launching marketing campaigns.
    """

    openaikey, age = prt.vault.get_secret("openaikey")
    api_key = openaikey

    llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0.3, streaming=False)

    slogans_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(payload.slogans)])
    prompt = f"""
You are a sentiment analysis assistant.

Evaluate the emotional sentiment of each of the following marketing slogans.

For each slogan, return a JSON object with the following fields:
- slogan
- sentiment (one of: positive, neutral, negative)
- comment (short explanation why)

Output a JSON array.

Slogans:
{slogans_text}
"""

    response = llm.invoke(prompt)
    response_text = response.content.strip()

    results = []
    for slogan in payload.slogans:
        slogan_lower = slogan.lower()
        sentiment = "neutral"
        comment = "Could not confidently extract sentiment."

        for line in response_text.splitlines():
            if slogan_lower[:10] in line.lower() or slogan_lower in line.lower():
                if "positive" in line.lower():
                    sentiment = "positive"
                elif "negative" in line.lower():
                    sentiment = "negative"
                elif "neutral" in line.lower():
                    sentiment = "neutral"
                comment = line.strip()
                break

        results.append(SloganSentimentResult(
            slogan=slogan,
            sentiment=sentiment,
            comment=comment
        ))

    return SentimentTestSloganResponse(results=results)
