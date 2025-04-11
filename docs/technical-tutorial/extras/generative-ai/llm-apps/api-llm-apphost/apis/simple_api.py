from pydantic import BaseModel
import practicuscore as prt
from practicuscore.gen_ai import PrtLangRequest, PrtLangMessage
from requests import get
import json

""" We are defining classes for taken inputs from api call. Using classes allows you to enforce type safety. 
This means you can be sure that the data your functions receive has the correct types and structure, 
reducing the likelihood of runtime errors. But you don't have to use classes while creating api scripts."""


# Holds a message's content and an optional role for model to consume prompts.
class Messages(PrtLangMessage):
    content: str
    role: str | None = None


# Stores details for a language model request, including the message, model type, and API information.
class ModelRequest(BaseModel):
    messages: Messages
    lang_model: str | None = "None"
    streaming: bool | None = False
    end_point: str
    api_token: str


# We need to define a 'run' function to process incoming data to API
@prt.apps.api("/simple-api")
async def run(payload: ModelRequest, **kwargs):
    # Set up authorization headers using the API token from the payload
    headers = {"authorization": f"Bearer {payload.api_token}"}

    # Create a language model request object with message, model, and streaming options
    practicus_llm_req = PrtLangRequest(
        messages=[payload.messages],
        lang_model=payload.lang_model,
        streaming=payload.streaming,
        llm_kwargs={"kw1": 123, "kw2": "k2"},
        # (Optional) Additional parameters for the language model could be added here
    )

    # Convert the request object to a JSON string, excluding unset fields
    data_js = json.loads(practicus_llm_req.model_dump_json(indent=2, exclude_unset=True))

    # Send the HTTP GET request to the specified endpoint with the headers and JSON data
    r = get(payload.end_point, headers=headers, json=data_js)

    # Parse the JSON response text into a Python dictionary
    parsed = json.loads(r.text)

    # Return the parsed response dictionary
    return parsed
