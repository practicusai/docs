---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Using Langflow APIs

- Login to Langflow service
- Create a flow
- Create an API endpoint name. e.g. my-api-endpoint
    - Click on flow name > Edit Details > Endpoint Name
- Get an access token using Practicus AI SDK
- Note the LLM model token as well, API calls do not use tokens you saved in the UI
- Make API calls

```python
service_url = "https://langflow.practicus.company.com"
# The below is defined in Langflow UI.
# Open a flow, click on flow name > Edit Details > Endpoint Name
endpoint_name = "my-api-endpoint"
```

```python
assert service_url, "Please define service_url"
assert endpoint_name, "Please define endpoint_name"

api_url = f"{service_url}/api/v1/run/{endpoint_name}?stream=false"
print("API url:", api_url)
# e.g. https://langflow.practicus.company.com/api/v1/run/api-test1?stream=false
```

```python
import practicuscore as prt

region = prt.current_region()
token = None  # Get a new token, or reuse existing if not expired.
access_token = region.get_addon_session_token(key="langflow", token=token)
```

```python
print("Access token for addon:", access_token)
```

```python
open_ai_token = ""
assert open_ai_token, "Please define open_ai_token"
```

```python
import requests

headers = {"Content-Type": "application/json", f"Authorization": f"Bearer {access_token}"}

payload = {
    "input_value": "message",
    "output_type": "chat",
    "input_type": "chat",
    "tweaks": {
        "ChatInput-MRIWj": {},
        "Prompt-KvhR7": {},
        "ChatOutput-CuWil": {},
        "OpenAIModel-dmT1W": {"api_key": open_ai_token},
    },
}

response = requests.post(api_url, headers=headers, json=payload)

print(response.status_code)
result = response.json()
print(result)
```


---

**Previous**: [Prtchatbot](../examples/prtchatbot/prtchatbot.md) | **Next**: [LLM Apps > API LLM Apphost > Build](../llm-apps/api-llm-apphost/build.md)
