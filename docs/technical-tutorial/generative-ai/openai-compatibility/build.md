---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus GenAI
    language: python
    name: practicus_genai
---

# OpenAI Compatibility

You can build Practicus AI APIs that are compatible with the OpenAI API endpoints and the SDK.

In this example, we demonstrate:
- Creating **Pydantic models** for ChatCompletion requests and responses.
- Deploying these models and building a proxy endpoint in Practicus AI.
- Sending requests to that proxy using **Python requests** and **OpenAI’s SDK**.


```python
# Convenience classes, you can also use your own that are compatible with OpenAI APIs.
from practicuscore.gen_ai import (
    ChatCompletionRequest, ChatMessage, ChatCompletionResponseUsage, ChatCompletionResponseChoiceMessage, 
    ChatCompletionResponseChoice, ChatCompletionResponse
)
```

```python
sample_request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="Hello!"),
    ],
    # You can also specify other optional fields, like temperature, max_tokens, etc.
)

# Convert request to JSON
request_json = sample_request.model_dump_json(indent=2)
print("Sample ChatGPT API request JSON:")
print(request_json)
```

```python
# Sample Response
# 1) Create a usage object
usage = ChatCompletionResponseUsage(
    prompt_tokens=5,
    completion_tokens=10,
    total_tokens=15
)

# 2) Create a message for the choice
choice_message = ChatCompletionResponseChoiceMessage(
    role="assistant",
    content="Hi there! How can I help you today?"
)

# 3) Create a choice object
choice = ChatCompletionResponseChoice(
    index=0,
    message=choice_message,
    finish_reason="stop"
)

# 4) Finally, create the top-level response object
response_obj = ChatCompletionResponse(
    id="chatcmpl-abc123",
    object="chat.completion",
    created=1700000000,
    model="gpt-3.5-turbo",
    usage=usage,
    choices=[choice]
)

# Convert response to JSON
response_json = response_obj.model_dump_json(indent=2)
print("Sample ChatGPT API response JSON:")
print(response_json)
```

```python
# Let's locate a model deployment in Practicus AI.
# This is environment-specific logic.

import practicuscore as prt

region = prt.get_default_region()

# Identify the first available model deployment system
if len(region.model_deployment_list) == 0:
    raise SystemError(
        "No model deployment systems are available. "
        "Please contact your system administrator."
    )
elif len(region.model_deployment_list) > 1:
    print("Multiple model deployment systems found. Using the first one.")

model_deployment = region.model_deployment_list[0]
deployment_key = model_deployment.key

# Identify the first available model prefix
if len(region.model_prefix_list) == 0:
    raise SystemError(
        "No model prefixes are available. "
        "Please contact your system administrator."
    )
elif len(region.model_prefix_list) > 1:
    print("Multiple model prefixes found. Using the first one.")

prefix = region.model_prefix_list[0].key

model_name = "openai-proxy"
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
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir
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
# Now let's send a test request to our proxy using Python's requests.
import requests 

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'application/json'
}

r = requests.post(api_url, headers=headers, data=request_json)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text} - {r.headers}")

print("Answer (dict):")
resp_dict = r.json()
print(resp_dict)

print("\nAnswer (Pydantic object):")
resp_object = ChatCompletionResponse.model_validate(resp_dict)
print(resp_object)
```

# Using OpenAI SDK

You can also install and use the **OpenAI Python SDK**, then override its URLs to point to the **Practicus AI** proxy endpoint.

```python
! pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url = api_url,   # The proxy URL deployed via Practicus
    api_key = token       # Practicus AI session token
)

print("Connecting to", client.base_url, "to test OpenAI SDK compatibility.")

response = client.chat.completions.create(
    model="llama2",  # Just an example model name
    messages=[
        {"role": "user", "content": "Testing SDK compatibility."},
    ]
)

print("\nResponse:")
print(response)

if response.choices:
    print("\nAssistant says:", response.choices[0].message.content)
```

### Using Practicus AI App Hosting

- Instead of Practicus AI’s **Model Hosting**, you can also use **App Hosting** to serve a custom Python file.
- For example, if your file is located at `apis/chat/completions.py`
- Then, you can set `base_url = "https://practicus.company.com/apps/my-openai-proxy/api"` in your OpenAI SDK config.
- The SDK calls `POST /chat/completions`, which your code handles internally to proxy OpenAI request.



## Supplementary Files

### model.py
```python
from practicuscore.gen_ai import (
    ChatCompletionRequest, ChatCompletionResponseUsage, ChatCompletionResponseChoiceMessage,
    ChatCompletionResponseChoice, ChatCompletionResponse
)

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    # Initialize your LLM model as usual


async def predict(payload_dict: dict, **kwargs):
    try:
        req = ChatCompletionRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid OpenAI ChatCompletionRequest request. {ex}") from ex

    msgs = ""
    for msg in req.messages:
        msgs += f"{(msg.role + ': ') if msg.role else ''}{msg.content}\n"

    # Usage (Optional)
    usage = ChatCompletionResponseUsage(
        prompt_tokens=5,
        completion_tokens=10,
        total_tokens=15
    )

    # Use your LLM model to generate a response.
    # This one just echoes back what the user asks.
    choice_message = ChatCompletionResponseChoiceMessage(
        role="assistant",
        content=f"You asked:\n{msgs}\nAnd I don't know how to respond yet."
    )

    # Create a choice object
    choice = ChatCompletionResponseChoice(
        index=0,
        message=choice_message,
        finish_reason="stop"
    )

    # Finally, create the top-level response object
    open_ai_compatible_response = ChatCompletionResponse(
        choices=[choice],
        # Optional, but recommended fields
        id="chatcmpl-abc123",
        model="gpt-3.5-turbo",
        usage=usage,
    )

    return open_ai_compatible_response

```


---

**Previous**: [Sample Vector Db](../vector-databases/sample-vector-db.md) | **Next**: [Distributed Computing > Introduction](../../distributed-computing/introduction.md)
