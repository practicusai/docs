---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Introduction

In this example, we will walk through the process of building a simple XGBoost model using a small dataset. We’ll begin by training and saving the model, and then demonstrate how to deploy it as a REST API endpoint. Finally, we’ll make some predictions by calling the deployed API.

By the end of this example, you will have a clear understanding of how to:

1. Prepare and train a basic XGBoost model.
2. Save the trained model to a file.
3. Deploy the model as a simple API service.
4. Make predictions by sending requests to the API.

This approach can be extended and adapted to more complex models and larger systems, giving you a foundation for building scalable machine learning services.


```python
# Let's build a simple XGBoost model

import pandas as pd
from xgboost import XGBRegressor

# Load the ice cream dataset that come pre-installed in Workers
df = pd.read_csv("/home/ubuntu/samples/ice_cream.csv")

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

```python
# Now let's decide where to deploy our model.
import practicuscore as prt 

region = prt.get_default_region()

# Let's locate the first available model deployment to deploy our model
if len(region.model_deployment_list) == 0:
    raise SystemError("You do not have any model deployment systems. "
                      "Please contact your system admin.")
elif len(region.model_deployment_list) > 1:
    print("You have more than one model deployment systems. "
          "Will use the first one")
model_deployment = region.model_deployment_list[0]
deployment_key = model_deployment.key

# Let's locate the first available model prefix to deploy our model
if len(region.model_prefix_list) == 0:
    raise SystemError("You do not have any model deployment systems. "
                      "Please contact your system admin.")
elif len(region.model_prefix_list) > 1:
    print("You have more than one model deployment systems. "
          "Will use the first one")

prefix = region.model_prefix_list[0].key

model_name = 'my-xgboost-model'
model_dir = None  # Current dir

# *All* Practicus AI model APIs follow the below url convention
api_url = f"{region.url}/{prefix}/{model_name}/"
# Important: For effective traffic routing, always terminate the url with / at the end.
print("Model REST API Url will be:", api_url)

print("We will deploy model the model using", deployment_key, "model deployment.")
```

### model.py
Now please review `model.py` file to see how the XGBoost model is consumed.

```python
# Time to deploy..
# You can call the below multiple times to deploy multiple versions
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir
)
```

```python
# We will be using using the SDK to get a session token.
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

```python
# Now let's consume the Rest API to make the prediction
import requests 

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv'
}
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
    model_file = os.path.join(current_dir, 'model.ubj')
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

**Previous**: [Workers](../../01_getting_started/02_workers.md) | **Next**: [Tasks](../../03_workflows/01_tasks/01_tasks.md)
