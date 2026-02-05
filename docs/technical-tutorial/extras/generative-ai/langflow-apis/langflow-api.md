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
run_id = None  # E.g. 861ef993-e360-4af8-b71d-a1494843d0a3
```

```python
assert service_url, "Please define service_url"
assert run_id, "Please define run_id"

api_url = f"{service_url}/api/v1/run/{run_id}?stream=false"
print("API url:", api_url)
# e.g. https://langflow.practicus.company.com/api/v1/run/861ef993-e360-4af8-b71d-a1494843d0a3
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

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}

payload = {
    "input_type": "chat",
    "output_type": "chat",
    "input_value": "Convert pineapple to uppercase using tools",
}

response = requests.post(api_url, headers=headers, json=payload)

print(response.status_code)
result = response.json()
print(result)
```


---

**Previous**: [Build](../langchain-legacy/langchain-serving/build.md) | **Next**: [LLM Apps > API LLM Apphost > Build](../llm-apps/api-llm-apphost/build.md)
