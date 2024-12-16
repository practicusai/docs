---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (for ML)
    language: python
    name: practicus_ml
---

# Model Observability and Monitoring
## _Scenario:_ Model Drift

In this example, we'll deploy a model on an insurance dataset to make two predictions. Introducing intentional drifts in the BMI and Age columns, we aim to observe their impact on the model's predictions.

1. _Open_ *Jupyter Notebook*
    
2. Train and deploy a model on insurance dataset

3. Making predictions with deployed model
    
4. Multiplying the BMI and Age columns to create Drifts on features and predictions

5. Observing the model drift plots


## Model Development


Loading and preparing the dataset

```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/insurance.csv"
}
```

```python
# Loading the dataset to worker

import practicuscore as prt

region = prt.current_region()
worker = region.get_or_create_worker()
proc = worker.load(data_set_conn) 

proc.show_head()
```

```python
# Pre-process

proc.categorical_map(column_name='sex', column_suffix='category') 
proc.categorical_map(column_name='smoker', column_suffix='category') 
proc.categorical_map(column_name='region', column_suffix='category') 
proc.delete_columns(['region', 'smoker', 'sex']) 
```

```python
# Taking the dataset into csv

df = proc.get_df_copy()
df.head()
```

Model Training

```python
X = df.drop('charges', axis=1)
y = df['charges']
```

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

```python
import xgboost as xgb
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('model', xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100))
])
pipeline.fit(X_train, y_train)
```

```python
# Exporting the model

import cloudpickle

with open('model.pkl', 'wb') as f:
    cloudpickle.dump(pipeline, f)
```

## Model Deployment

```python
# Please ask for a deployment key from your admin.
deployment_key = ""
assert deployment_key, "Please select a deployment_key"
prefix = "models"
model_name = "custom-insurance-test"
model_dir= None  # Current dir 
```

```python
prt.models.deploy(
    deployment_key=deployment_key, 
    prefix=prefix, 
    model_name=model_name, 
    model_dir=model_dir
)
```

## Prediction

```python
# Loading the dataset to worker

import practicuscore as prt

region = prt.current_region()
worker = region.get_or_create_worker()
proc = worker.load(data_set_conn) 

proc.categorical_map(column_name='sex', column_suffix='category') 
proc.categorical_map(column_name='smoker', column_suffix='category') 
proc.categorical_map(column_name='region', column_suffix='category') 
proc.delete_columns(['region', 'smoker', 'sex']) 

df = proc.get_df_copy()
df.head()
```

```python
# Let's construct the REST API url.
# Please replace the below url with your current Practicus AI address
# e.g. http://practicus.company.com
practicus_url = ""  
assert practicus_url, "Please select practicus_url"
# *All* Practicus AI model APIs follow the below url convention
api_url = f"https://{practicus_url}/{prefix}/{model_name}/"
# Important: For effective traffic routing, always terminate the url with / at the end.
print("Model REST API Url:", api_url)
```

```python
# We will be using using the SDK to get a session token.
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

```python
import requests
import pandas as pd

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv'
}
data_csv = df.to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO
pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```

- After you make the first prediction, please wait for 5 minutes to see a clearer picture on the drift plot
- When we look at Model Drifts Dashboard at Grafana we will see plots with the model drift visible


## Hand-Made Model Drift

```python
df['age'] = df['age'] * 2
```

```python
df['bmi'] = df['bmi'] * 3
```

```python
display(df)
```

```python
headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv'
}
data_csv = df.to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```

- After you make the second prediction, please wait for 2 minutes to see a clearer picture on the drift plot
- When we look at Model Drifts Dashboard at Grafana we will see plots with the model drift visible


## Supplementary Files

### model.py
```python
import os
from typing import Optional
import pandas as pd
from starlette.exceptions import HTTPException
import joblib 


model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: Optional[pd.DataFrame] = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise HTTPException(status_code=500, detail="No dataframe received")

    if 'charges' in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop('charges', axis=1)  

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predictions'])
    
    return predictions_df

```


---

**Previous**: [Experiment Tracking Model Training](../experiment-tracking/experiment-tracking-model-training.md) | **Next**: [Model Observability](../../model-observability/model-observability.md)
