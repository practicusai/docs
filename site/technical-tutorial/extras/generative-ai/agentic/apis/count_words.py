import practicuscore as prt
from pydantic import BaseModel, Field


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


@prt.api("/count-words")
async def run(payload: CountWordsRequest, **kwargs) -> CountWordsResponse:
    """Count the number of words in the given text."""
    word_count = len(payload.text.split())
    return CountWordsResponse(word_count=word_count)
