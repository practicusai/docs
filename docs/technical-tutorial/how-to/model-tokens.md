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

# Using model access tokens

- In this example we will show how to find model prefixes, models and get short lived session tokens.

#### Anatomy of a model url 

- Practicus services follow this pattern:
    - [ primary service url ] / [ model prefix ] / [ model name ] / < optional version > /
- Sample model addresses:
    - https://practicus.company.com/models/practicus/diamond-price/
    - https://practicus.company.com/models/practicus/diamond-price/v3/
- Please note that Practicus AI model urls always end with a "/" 


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
model_name = None  # E.g. "diamond-price"
model_prefix = None  #  E.g. 'models/practicus'
```

```python
assert model_name, "Please enter your model_name "
assert model_prefix, "Please enter your model_prefix."
```

```python
import practicuscore as prt

region = prt.regions.get_default_region()
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


filtered_df = df[(df["prefix"] == model_prefix) & (df["versions"].notna())]
display(filtered_df)
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

from requests.models import Response
import requests

# Option 1 - Use password auth every time you need tokens
console_api_url = "http://local.practicus.io/console/api/"
email = "admin@admin.com"
password = "admin"

data = {"email": email, "password": password}
console_login_api_url = f"{console_api_url}auth/"

try:
    r: Response = requests.post(console_login_api_url, json=data)
    r.raise_for_status() # HATA 3: HTTP hatalarını yakalamak için en Pythonic yöntem budur.
except requests.exceptions.RequestException as e:
    print(f"Login Failed: {e}")
    # Login başarısızsa devam etmenin anlamı yok
    exit(1)

body = r.json()
refresh_token = body["refresh"]
console_access_token = body["access"]

# Option 2 - Get a refresh token once
print("[Recommended] Getting console API access token using refresh token")
console_access_api_url = f"{console_api_url}auth/refresh/"

# Headers
headers = {"authorization": f"Bearer {refresh_token}"}
data = {"refresh": refresh_token}

try:
    r = requests.post(console_access_api_url, headers=headers, json=data)
    r.raise_for_status()
    body = r.json()
    console_access_token = body["access"]
    
    # Update access token
    headers = {"authorization": f"Bearer {console_access_token}"}
    print("Console API access token:", console_access_token)

    # Locating model id
    print("Getting model id from metadata...")
    r = requests.get(f"{api_url}?get_meta=true", headers=headers)
    r.raise_for_status()

    model_id = int(r.headers.get("x-prt-model-id", 0))
    
    if model_id == 0:
        raise ValueError("Model ID could not be found in headers.")
        
    print("Model id:", model_id)

    # Getting model access token
    print("Getting a model API session token using the console API access token")
    console_model_token_api_url = f"{console_api_url}modelhost/model-auth/"
    
    auth_data = {"model_id": model_id}
    r = requests.get(console_model_token_api_url, headers=headers, json=auth_data)
    r.raise_for_status()
    
    body = r.json()
    model_api_token = body.get("token")
    print("✅ Model API session token:", model_api_token)

except requests.exceptions.RequestException as e:
    print(f"❌ Connection or API Error: {e}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
```


---

**Previous**: [MCP Langgraph](mcp-langgraph.md) | **Next**: [Personal Startup Scripts](personal-startup-scripts.md)
