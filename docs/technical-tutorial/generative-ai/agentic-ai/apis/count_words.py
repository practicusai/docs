# apis/count_words.py
import practicuscore as prt
from pydantic import BaseModel


class CountWordsRequest(BaseModel):
    text: str
    """The text in which to count words."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"text": "Hello world, this is a test."}]},
    }


class CountWordsResponse(BaseModel):
    word_count: int
    """The number of words in the provided text."""

    model_config = {"use_attribute_docstrings": True, "json_schema_extra": {"examples": [{"word_count": 6}]}}


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/count-words", spec=api_spec)
async def run(payload: CountWordsRequest, **kwargs) -> CountWordsResponse:
    """Count the number of words in the given text."""
    word_count = len(payload.text.split())
    return CountWordsResponse(word_count=word_count)
