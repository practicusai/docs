---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Hosting of LLM application on AppHost without using front-end.

In this example we will try to host an LLM application which only used by API requests. This application will use an already deployed llm model.



### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
host = None  # E.g. 'company.practicus.com'
lang_model = None  # E.g. 'LLAMA-3-70b'
app_name = None  # E.g. 'api-chatbot'
model_name = None
model_prefix = None
deployment_setting_key = None
app_prefix = None
```

```python
assert host, "Please enter your host url"
assert lang_model, "Please select a model"
assert app_name, "Please enter application name"
assert model_name, "Please enter model_name"
assert model_prefix, "Please enter model_prefix"
assert deployment_setting_key, "Please enter deployment_setting_key"
assert app_prefix, "Please enter app_prefix"
```

```python
import practicuscore as prt
import requests
import json

region = prt.get_region()
```

#### API Python script

First of all we need to create a Python scripts which will be invoked by using requests. For this instance we should create an 'apis' folder which will contain the Python scripts. Then we can create our scripts within the folder.

You can check-out sample api script [simple_api.py](apis/simple_api.py)


If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
# Let's list our models and select one of them.
my_model_list = region.model_list
display(my_model_list.to_pandas())
```

```python
# Let's list our model prefixes and select one of them.
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
```

```python
# Let's list our app deployments and select one of them.
my_app_settings = prt.apps.get_deployment_setting_list()
display(my_app_settings.to_pandas())
```

```python
# Let's list our app prefixes and select one of them.
my_app_prefix_list = prt.apps.get_prefix_list()
display(my_app_prefix_list.to_pandas())
```

#### Testing scripts

We can call our api scripts withIn this example and test them

```python
api_url = f"https://{host}/{model_prefix}/{model_name}/"
token = prt.models.get_session_token(api_url=api_url)
```

```python
from apis.simple_api import Messages, ModelRequest, run

# Let's test our message class
messages = Messages(content="Who is einstein?", role="human")

messages
```

```python
# Let's test our Model request class
modelreq = ModelRequest(messages=messages, lang_model=lang_model, streaming=False, api_token=token, end_point=api_url)

dict(modelreq)
```

```python
# Let's test our prediction function
response = run(modelreq)

dict(response)
```

#### Deployment of API

After testing our python scripts, and make sure they work, we can deploy them by using our prefix and SDK

```python
prt.apps.deploy(
    deployment_setting_key=deployment_setting_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,  # Current dir
)
```

#### Prediction by using API

After the deployment process we can consume the api url by using the code cell down below

```python
api_url = f"https://{host}/{app_prefix}/{app_name}/api/simple_api/"
token = None  # Get a new token, or reuse existing if not expired.
token = prt.apps.get_session_token(api_url=api_url, token=token)
```

```python
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}


data_js = modelreq.model_dump_json(indent=2)

resp = requests.post(api_url, json=data_js, headers=headers)

if resp.ok:
    print(f"Response text:", resp.text)
else:
    print(resp.status_code, resp.text)
```

After deployment, comprehensive documentation for the API service is automatically generated. You can review this documentation and easily share it with your colleagues and other team members for seamless collaboration and onboarding.

```python
documentation_url = f"https://{host}/{app_prefix}/{app_name}/api/redoc/"
print(f"Your documentation url:{documentation_url}")
```


## Supplementary Files

### apis/simple_api.py
```python
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

```


---

**Previous**: [Langflow API](../../langflow-apis/langflow-api.md) | **Next**: [Sdk LLM Apphost > Non Stream > Sdk Streamlit Hosting](../sdk-llm-apphost/non-stream/sdk-streamlit-hosting.md)
