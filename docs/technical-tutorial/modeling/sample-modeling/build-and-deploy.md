---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
model_deployment_key = None
model_prefix = None
```

```python
assert model_deployment_key, "Please provide model deployment key for classic ML modeling"
assert model_prefix, "Please provide model prefix for classic ML modeling"
```

# Building and deploying an XGBoost model

In this example, we will walk through the process of building a simple XGBoost model using a small dataset. We’ll begin by training and saving the model, and then demonstrate how to deploy it as a REST API endpoint. Finally, we’ll make some predictions by calling the deployed API.

By the end of this example, you will have a clear understanding of how to:

1. Prepare and train a basic XGBoost model.
2. Save the trained model to a file.
3. Deploy the model as a simple API service.
4. Make predictions by sending requests to the API.

This approach can be extended and adapted to more complex models and larger systems, giving you a foundation for building scalable machine learning services.

### Sample XGBoost model 

Let's build a simple XGBoost model

```python
import pandas as pd
from xgboost import XGBRegressor

# Load the ice cream dataset that come pre-installed in Workers
df = pd.read_csv("/home/ubuntu/samples/data/ice_cream.csv")

# Separate features and target
X = df[["Temperature"]]
y = df["Revenue"]

# Create and train the XGBoost regressor
model = XGBRegressor(n_estimators=50)
model.fit(X, y)

# Save the model using the recommended XGBoost .ubj format
model.save_model("model.ubj")

print("Model saved as model.ubj")
```

<!-- #region -->
### How to Query for Deployments and Prefixes

If you are unsure about which model deployment (the underlying infrastructure) or which logical address group (prefix) to use, you can run the code below to dynamically query the available options.

If you already have the required information, you can define it directly as shown here and skip the query step:

```python
deployment_key = "some-deployment"
prefix = "models"
```

The code below demonstrates how to programmatically identify the first available model deployment system and model prefix. These values are then used to construct a URL for deploying and accessing a model’s REST API.
<!-- #endregion -->

```python
# Let's select a unique model name.
# Note: Deployment will fail if you use an existing model name, under the same model prefix,
# and you are not the owner of the existing model to deploy a new model version for.
import praticuscore as prt

region = prt.get_default_region()
my_user_name = region.username
model_name = f"xgboost-model-{my_user_name}"
```

```python
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

model_dir = None  # Use the current directory by default

# All Practicus AI model APIs follow this URL convention:
expected_api_url = f"{region.url}/{model_prefix}/{model_name}/"
# Note: Ensure the URL ends with a slash (/) to support correct routing.

print("Expected Model REST API URL:", expected_api_url)
print("Using model deployment:", model_deployment_key)
```

### model.py

Review the `model.py` file to see how the XGBoost model is integrated and consumed within the environment.

### Deploy the model as an API

```python
# This function can be called multiple times to deploy additional versions.
api_url, api_version_url, api_meta_url = prt.models.deploy(
    deployment_key=model_deployment_key, prefix=model_prefix, model_name=model_name, model_dir=model_dir
)
```

```python
print("Which model API URL to use:")
print("If you prefer the system admin dynamically route")
print("  between model versions (recommended), use the below:")
print(api_url)
print("If you prefer to use exactly this version, use the below:")
print(api_version_url)
print("If you prefer to get the metadata of this version, use the below:")
print(api_meta_url)
```

### Making predictions using the model API

```python
# We will be using using the SDK to get a session token (or reuse existing, if not expired).
# To learn how to get a token without the SDK, please view samples in the extras section
token = None
token = prt.models.get_session_token(api_url, token=token)
print("API session token:", token)
```

```python
# Now let's consume the Rest API to make the prediction
import requests

headers = {"authorization": f"Bearer {token}", "content-type": "text/csv"}
data_csv = df["Temperature"].to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text} - {r.headers}")

from io import BytesIO

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
display(pred_df)
```


## Supplementary Files

### model.py
```python
import os
import pandas as pd
from xgboost import XGBRegressor

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, "model.ubj")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model = XGBRegressor()
    model.load_model(model_file)


async def predict(df, *args, **kwargs):
    if df is None:
        raise ValueError("No dataframe received")

    X = df[["Temperature"]]

    # Generate predictions
    predictions = model.predict(X)

    # Return predictions as a new DataFrame
    return pd.DataFrame({"predictions": predictions})

```


---

**Previous**: [Introduction](../introduction.md) | **Next**: [Workflows > Introduction](../../workflows/introduction.md)
