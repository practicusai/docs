---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Hosting of LLM application on AppHost without using front-end.

In this example we will try to host an LLM application which only used by API requests. This application will use an already deployed llm model.


```python
import practicuscore as prt
import requests 
import json
```

#### API Python script

First of all we need to create a Python scripts which will be invoked by using requests. For this instance we should create an 'apis' folder which will contain the Python scripts. Then we can create our scripts within the folder.

You can check-out sample api script [simple_api.py](apis/simple_api.py)


## Define params from region

```python
host = 'preview.practicus.io' # Example url -> 'company.practicus.com'
assert host, "Please enter your host url" 

lang_model= 'LLAMA-3-70b'
assert lang_model, "Please select a model"

app_name = 'api-chatbot'
assert app_name, "Please enter application name"
```

```python
region = prt.get_region()

# Let's list our models and select one of them.
my_model_list = region.model_list
display(my_model_list.to_pandas())

# We will select second model
model_name = my_model_list[1].name
print("Using second model name:", model_name)
```

```python
# Let's list our model prefixes and select one of them.
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())

# We will select first prefix
model_prefix = my_model_prefixes[0].key
print("Using first prefix:", model_prefix)
```

```python
# Let's list our app deployments and select one of them.
my_app_settings = region.app_deployment_setting_list
display(my_app_settings.to_pandas())

# We will select the first deployment
deployment_setting_key = my_app_settings[0].key
print("Using first setting with key:", deployment_setting_key)
```

```python
# Let's list our app prefixes and select one of them.
my_app_prefix_list = region.app_prefix_list
display(my_app_prefix_list.to_pandas())

# We will select first prefix
app_prefix = my_app_prefix_list[0].prefix
print("Using first app prefix", app_prefix)
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
messages = Messages(
    content="Who is einstein?", 
    role="human"
)

messages
```

```python
# Let's test our Model request class
modelreq = ModelRequest(
    messages = messages,
    lang_model = lang_model,
    streaming = False,
    api_token = token,
    end_point = api_url
)

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
    app_dir=None # Current dir
)
```

#### Prediction by using API

After the deployment process we can consume the api url by using the code cell down below

```python
api_url = f"https://{host}/{app_prefix}/{app_name}/api/simple_api/"
token = prt.apps.get_session_token(api_url=api_url)
```

```python
headers = {
    "Authorization": f"Bearer {token}",
    "content-type": 'application/json'}


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
from practicuscore.gen_ai import PrtLangRequest, PrtLangMessage
from requests import get
import json

''' We are defining classes for taken inputs from api call. Using classes allows you to enforce type safety. 
This means you can be sure that the data your functions receive has the correct types and structure, 
reducing the likelihood of runtime errors. But you don't have to use classes while creating api scripts.'''

# Holds a message's content and an optional role for model to consume prompts.
class Messages(PrtLangMessage):
    content: str
    role: str | None = None

# Stores details for a language model request, including the message, model type, and API information.
class ModelRequest(BaseModel):
    messages: Messages
    lang_model: str | None = 'None'
    streaming: bool | None = False
    end_point: str
    api_token: str

# We need to define a 'run' function to process incoming data to API
def run(payload: ModelRequest, **kwargs):

    # Set up authorization headers using the API token from the payload
    headers = {'authorization': f'Bearer {payload.api_token}'}

    # Create a language model request object with message, model, and streaming options
    practicus_llm_req = PrtLangRequest(
        messages=[payload.messages],
        lang_model=payload.lang_model,
        streaming=payload.streaming,
        llm_kwargs={"kw1": 123, "kw2": "k2"} # (Optional) Additional parameters for the language model could be added here
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

**Previous**: [Lang Chain LLM Model](../../advanced-langchain/lang-chain-llm-model.md) | **Next**: [Sdk LLM Apphost > Non Stream > Sdk Streamlit Hosting](../sdk-llm-apphost/non-stream/sdk-streamlit-hosting.md)
