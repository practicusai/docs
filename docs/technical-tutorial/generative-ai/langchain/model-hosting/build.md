---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Deploying Langchain compatible LLM model

In this example we will be deploying a dummy model compatible with Langchain. Please also view OpenAI compatibility section to deploy LLM APIs that are compatible with OpenAI SDK.

```python
# Let's locate a model deployment in Practicus AI.
# This is environment-specific logic.

import practicuscore as prt

region = prt.get_default_region()

# Identify the first available model deployment system
if len(region.model_deployment_list) == 0:
    raise SystemError("No model deployment systems are available. Please contact your system administrator.")
elif len(region.model_deployment_list) > 1:
    print("Multiple model deployment systems found. Using the first one.")

model_deployment = region.model_deployment_list[0]
deployment_key = model_deployment.key

# Identify the first available model prefix
if len(region.model_prefix_list) == 0:
    raise SystemError("No model prefixes are available. Please contact your system administrator.")
elif len(region.model_prefix_list) > 1:
    print("Multiple model prefixes found. Using the first one.")

prefix = region.model_prefix_list[0].key

model_name = "practicus-llm"
model_dir = None  # Use the current directory by default

# Construct the URL. Ensure it ends with a slash.
expected_api_url = f"{region.url}/{prefix}/{model_name}/"

print("Expected Model REST API URL:", expected_api_url)
print("Using model deployment:", deployment_key)
```

## model.py

For the sake simplicity, we are deploying a model that just echoes what we send.

```python
# Deploy model.py
api_url, api_version_url, api_meta_url = prt.models.deploy(
    deployment_key=deployment_key, prefix=prefix, model_name=model_name, model_dir=model_dir
)
```

```python
print("Which model API URL to use:")
print("- To let the system dynamically route between versions (recommended):")
print(api_url)

print("\n- To use exactly this version:")
print(api_version_url)

print("\n- For metadata on this version:")
print(api_meta_url)
```

```python
# We'll use the Practicus AI SDK to get a session token.
# If you prefer, you can handle authentication differently.
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

```python
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse

human_msg = PrtLangMessage(content="Who is einstein? ", role="human")

system_msg = PrtLangMessage(content="Give me answer less than 100 words.", role="system")

practicus_llm_req = PrtLangRequest(
    # Our context
    messages=[human_msg, system_msg],
    # Select a model, leave empty for default
    lang_model="",
    # Streaming mode
    streaming=True,
    # If we have a extra parameters at model.py we can add them here
    llm_kwargs={"kw1": 123, "kw2": "k2"},
)

request_json = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)

print("Will send json request:")
print(request_json)
```

```python
# Now let's send a test request to our proxy using Python's requests.
import requests

headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}

r = requests.post(api_url, headers=headers, data=request_json)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text} - {r.headers}")

print("Answer (dict):")
resp_dict = r.json()
print(resp_dict)

print("\nAnswer (Pydantic object):")
resp_object = PrtLangResponse.model_validate(resp_dict)
print(resp_object)
```

```python

```


## Supplementary Files

### model.py
```python
from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse
import json

model = None


async def init(model_meta=None, *args, **kwargs):
    print("Initializing model")
    global model
    # Initialize your LLM model as usual


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")
    # Add your clean-up code here


async def predict(payload_dict: dict, **kwargs):
    try:
        req = PrtLangRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid PrtLangRequest request. {ex}") from ex

    # Converts the validated request object to a dictionary.
    data_js = req.model_dump_json(indent=2, exclude_unset=True)
    payload = json.loads(data_js)

    # Joins the content field from all messages in the payload to form the prompt string.
    prompt = " ".join([item["content"] for item in payload["messages"]])

    answer = f"You asked:\n{prompt}\nAnd I don't know how to respond yet."

    resp = PrtLangResponse(
        content=answer,
        lang_model=payload["lang_model"],
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        # additional_kwargs={
        #     "some_additional_info": "test 123",
        # },
    )

    return resp

```


---

**Previous**: [Streaming](../streaming.md) | **Next**: [Embeddings](../embeddings.md)
