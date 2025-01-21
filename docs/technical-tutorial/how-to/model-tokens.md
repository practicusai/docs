---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Using model access tokens

- In this example we will show how to find model prefixes, models and get short lived session tokens.

#### Anatomy of a model url 

- Practicus services follow this pattern:
    - [ primary service url ] / [ model prefix ] / [ model name ] / < optional version > /
- Sample model addresses:
    - https://service.practicus.io/models/practicus/diamond-price/
    - https://service.practicus.io/models/practicus/diamond-price/v3/
- Please note that Practicus AI model urls always end with a "/" 

```python
import practicuscore as prt 

region = prt.regions.get_default_region()
```

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
model_name = None # E.g. "diamond-price"
model_prefix = None #  E.g. 'models/practicus'
```

```python
assert model_name, "Please enter your model_name "
assert model_prefix, "Please enter your model_prefix."
```

```python
# Let's get model prefixes dataframe
# We can also use the list form with: region.model_prefix_list 
model_prefix_df = region.model_prefix_list.to_pandas()

print("Current model prefixes:")
print("Note: we will use the 'prefix' column in the API urls, and not the 'key'.")

display(model_prefix_df)
```

```python
print("Current models:")
print("Note: we will use the 'name' column in the API urls, and not 'model_id'")

df = region.model_list.to_pandas()
display(df)
```

```python
# You can use regular pandas filters
# E.g. let's search for models with a particular model prefix, 
# and remove all models that are not deployed (hs no version)


filtered_df = df[(df['prefix'] == model_prefix) & (df['versions'].notna())]
display(filtered_df)
```

```python
assert model_name, "Please enter your model_name"
assert model_prefix, "Please enter your model_prefix"
```

```python
api_url = f"{region.url}/{model_prefix}/{model_name}/"

print("Getting Model API session token for:", api_url)
token = prt.models.get_session_token(api_url)

print("Model access token with a short life:")
print(token)
```

### Getting Model API session token using REST API calls
If your end users do not have access to Practicus AI SDK, they can simply make the below REST API calls with **any programming language** to get a Model API session token.

```python
# "No Practicus SDK" sample to get a session token

import requests

try :
    console_api_url = "http://local.practicus.io/console/api/"

    # Option 1 - Use password auth every time you need tokens
    print("[Not Recommended] Getting console API access token using password.")
    email = "admin@admin.com"
    password = "admin"

    data = {"email": email, "password": password}
    console_login_api_url = f"{console_api_url}auth/"
    r = requests.post(console_login_api_url, headers=headers, json=data)
    if not r.ok:
        raise ConnectionError(r.status_code)
    body = r.json()
    refresh_token = body["refresh"]  # Keep refresh tokens safe!
    console_access_token = body["access"] 

    # Option 2 - Get a refresh token once, and only use that until it expires in ~3 months
    print("[Recommended] Getting console API access token using refresh token")
    console_access_api_url = f"{console_api_url}auth/refresh/"
    headers = {"authorization": f"Bearer {refresh_token}"}
    data = {"refresh": refresh_token}
    r = requests.post(console_access_api_url, headers=headers, json=data)
    if not r.ok:
        raise ConnectionError(r.status_code)
    body = r.json()
    console_access_token = body["access"]
    headers = {"authorization": f"Bearer {console_access_token}"}

    # Console API access tokens expire in ~30 minutes
    print("Console API access token:", console_access_token)

    # Locating model id
    print("Getting model id.")
    print("Note: you can also view model id using Open API documentation (E.g. https://../models/redoc/), or using Practicus AI App.")
    r = requests.get(api_url + "?get_meta=true", headers=headers, data=data)
    if not r.ok:
        raise ConnectionError(r.status_code)
    model_id = int(r.headers["x-prt-model-id"])
    print("Model id:", model_id)

    # Getting model access token, expires in ~4 hours
    print("Getting a model API session token using the console API access token") 
    console_model_token_api_url = f"{console_api_url}modelhost/model-auth/"
    data = {"model_id": model_id}
    r = requests.get(console_model_token_api_url, headers=headers, data=data)
    if not r.ok:
        raise ConnectionError(r.status_code)
    body = r.json()
    model_api_token = body["token"]
    print("Model API session token:", model_api_token) 
except:
    pass
```


---

**Previous**: [Create Virtual Envs](create-virtual-envs.md) | **Next**: [Use Polars](use-polars.md)
