---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# OpenAI Compatibility for embeddings

You can build Practicus AI embedding APIs that are compatible with the OpenAI API embedding endpoints and the SDK.

```python
model_deployment_key = None
model_prefix = None
```

```python
assert model_deployment_key, "Please provide model deployment key for embeddings model modelhost"
assert model_prefix, "Please provide model prefix for embeddings model modelhost"
```

```python
# Convenience classes, you can also use your own that are compatible with OpenAI APIs.
from practicuscore.gen_ai import PrtEmbeddingsRequest, PrtEmbeddingObject, PrtEmbeddingUsage, PrtEmbeddingsResponse
```

```python
sample_request = PrtEmbeddingsRequest(
    input=[
        "This is a text to create embeddings of.",
        "This is another text to do the same.",
    ],
    # Optional parameters
    # model="an-optional-model-id",
    # user="an-optional-user-id",
)

# Convert request to JSON
request_json = sample_request.model_dump_json(indent=2)
print("Sample ChatGPT compatible embedding API request JSON:")
print(request_json)
```

```python
# Sample Response
# 1) Create a usage object
usage = PrtEmbeddingUsage(prompt_tokens=5, total_tokens=15)

# 2) # let's simulate embeddings and index.
embedding = PrtEmbeddingObject(embedding=[0.123, 0.345], index=123)

# 4) Finally, create the top-level response object
response_obj = PrtEmbeddingsResponse(
    data=[embedding],
    model="an-optional-model-id",
    usage=usage,
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

if not model_deployment_key:
    # Identify the first available model deployment system
    if len(region.model_deployment_list) == 0:
        raise SystemError("No model deployment systems are available. Please contact your system administrator.")
    elif len(region.model_deployment_list) > 1:
        print("Multiple model deployment systems found. Using the first one.")
    model_deployment = region.model_deployment_list[0]
    model_deployment_key = model_deployment.key

if not model_prefix:
    # Identify the first available model prefix
    if len(region.model_prefix_list) == 0:
        raise SystemError("No model prefixes are available. Please contact your system administrator.")
    elif len(region.model_prefix_list) > 1:
        print("Multiple model prefixes found. Using the first one.")

    model_prefix = region.model_prefix_list[0].key

model_name = "openai-embedding-proxy"
model_dir = None  # Use the current directory by default

# Construct the URL. Ensure it ends with a slash.
expected_api_url = f"{region.url}/{model_prefix}/{model_name}/"

print("Expected Model REST API URL:", expected_api_url)
print("Using model deployment:", model_deployment_key)
```

## model.py

For the sake simplicity, we are deploying a model that sends random embeddings.

```python
# Deploy model.py
api_url, api_version_url, api_meta_url = prt.models.deploy(
    deployment_key=model_deployment_key, prefix=model_prefix, model_name=model_name, model_dir=model_dir
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
token = None  # Get a new token, or reuse existing, if not expired
token = prt.models.get_session_token(api_url, token=token)
print("API session token:", token)
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
resp_object = PrtEmbeddingsResponse.model_validate(resp_dict)
print(resp_object)
```

# Using OpenAI SDK

You can also install and use the **OpenAI Python SDK**, then override its URLs to point to the **Practicus AI** proxy endpoint.

```python
! pip install openai
```

```python
from openai import OpenAI

client = OpenAI(base_url=api_url, api_key=token)

print("Connecting to", client.base_url, "to test OpenAI SDK compatibility for embeddings.")

try:
    response = client.embeddings.create(
        model="some-model-id",
        input=["Testing embedding SDK compatibility."],
        # user="optional-username",
    )

    print("\nResponse:")
    print(response)

    if response.data:
        print(
            "\nEmbedding vector (first 5 elements):", response.data[0].embedding[:5]
        )  # Print the first 5 elements of the embedding

except Exception as e:
    print(f"An error occurred: {e}")
```

### Using Practicus AI App Hosting

- Instead of Practicus AI’s **Model Hosting**, you can also use **App Hosting** to serve a custom Python file.
- For example, if your file is located at `apis/chat/completions.py`
- Then, you can set `base_url = "https://practicus.company.com/apps/my-embedding/api"` in your OpenAI SDK config.




## Supplementary Files

### model.py
```python
from practicuscore.gen_ai import PrtEmbeddingsRequest, PrtEmbeddingObject, PrtEmbeddingUsage, PrtEmbeddingsResponse

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    # Initialize your embedding model as usual


async def predict(payload_dict: dict, **kwargs):
    try:
        req = PrtEmbeddingsRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid PrtEmbeddingsRequest request. {ex}") from ex

    usage = PrtEmbeddingUsage(prompt_tokens=5, total_tokens=15)

    # Generating some random embeddings, replace with the actual model
    embedding = PrtEmbeddingObject(embedding=[0.123, 0.345, 0.567, 0.789], index=1234)

    response_obj = PrtEmbeddingsResponse(
        data=[embedding],
        model="an-optional-model-id",
        usage=usage,
    )

    return response_obj

```


---

**Previous**: [Build](../models/build.md) | **Next**: [LangChain > Build](../langchain/build.md)
