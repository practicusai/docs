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


# Data Loading and Pre-Processing with Practicus Core
This code demonstrates how to load, preprocess, and prepare a dataset for machine learning:
1. **Dataset Connection**: 
   - Specifies the connection type (`WORKER_FILE`) and the path to the dataset file (`insurance.csv`).
2. **Load Dataset**: 
   - Imports the Practicus Core library.
   - Retrieves or creates a worker in the current region.
   - Loads the dataset into the worker.
   - Displays the first few rows of the dataset using `proc.show_head()`.
3. **Pre-processing**:
   - Applies categorical mapping to columns (`sex`, `smoker`, `region`) to create new categorical columns.
   - Deletes the original columns (`region`, `smoker`, `sex`) after mapping.
4. **Export Dataset**:
   - Retrieves a copy of the preprocessed dataset as a DataFrame.
   - Displays the first few rows of the modified dataset.
5. **Feature-Target Separation**:
   - Defines `X` as the feature set by dropping the `charges` column.
   - Defines `y` as the target variable (`charges`).


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

# Train-Test Split, Model Training, and Export
This code handles the following tasks:
1. **Train-Test Split**:
   - The dataset is divided into training and testing subsets using an 80-20 split.
2. **Pipeline Creation**:
   - Creates a machine learning pipeline using `Pipeline` from `sklearn`.
   - Includes an `XGBRegressor` model configured for regression with the `reg:squarederror` objective and 100 estimators.
3. **Model Training**:
   - Fits the pipeline to the training data (`X_train`, `y_train`).
4. **Model Export**:
   - Serializes and saves the trained pipeline using `cloudpickle` to a file named `model.pkl`, enabling reuse of the trained model for future predictions.


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

# Model Deployment with Practicus
This code demonstrates how to deploy a trained model using Practicus:
1. **Deployment Key**:
   - A `deployment_key` is required for authorization. It must be obtained from the administrator.
   - An assertion ensures that the `deployment_key` is set; otherwise, an error is raised.
2. **Model Deployment Configuration**:
   - `prefix`: Specifies the prefix for organizing the deployed models.
   - `model_name`: Sets a custom name for the deployed model (`custom-insurance-test`).
   - `model_dir`: Optionally specifies the directory of the model. If `None`, the current directory is used.
3. **Deploy Model**:
   - The `prt.models.deploy()` function is used to deploy the model with the provided parameters.


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

# Dataset Preparation, Model API Construction, and Prediction
This code performs the following tasks:
1. **Load and Preprocess Dataset**:
   - Imports the Practicus Core library and initializes the worker.
   - Loads the dataset and applies categorical mappings to specific columns (`sex`, `smoker`, `region`).
   - Deletes the original columns post-mapping to avoid redundancy.
   - Retrieves the preprocessed dataset as a DataFrame.
2. **Construct the REST API URL**:
   - Constructs the REST API URL for the deployed model. 
   - Requires the `practicus_url` (base URL of the Practicus AI platform) and other parameters (`prefix`, `model_name`).
   - Ensures the URL ends with a `/` for proper routing.
3. **Get Session Token**:
   - Retrieves an API session token using the Practicus AI SDK.
   - Prints the token for reference.
4. **Send Data for Prediction**:
   - Sends the preprocessed dataset to the model REST API in CSV format using a `POST` request.
   - Includes necessary headers, such as authorization (`Bearer` token) and content type (`text/csv`).
   - Handles any connection errors that may occur.
5. **Receive and Display Predictions**:
   - Reads the response from the API and converts it into a DataFrame.
   - Prints the first few rows of the prediction results for review.


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


# Simulating Model Drift and Analyzing
This section of the code introduces artificial model drift and demonstrates how to evaluate its effects:
1. **Hand-Made Model Drift**:
   - Artificially modifies the dataset by altering the `age` and `bmi` columns (multiplying by 2 and 3, respectively).
   - Displays the modified dataset for verification.
2. **Send Modified Data for Prediction**:
   - Prepares the modified dataset as a CSV file.
   - Sends it to the deployed model API using a `POST` request with proper authorization headers.
   - Checks for errors during the request.
3. **Analyze Predictions**:
   - Reads the API's prediction response into a DataFrame.
   - Displays the prediction results to analyze the impact of drift on the model's outputs.
4. **Monitor Drift on Grafana**:
   - After the second prediction, wait for 2 minutes to allow for drift detection updates.
   - View the **Model Drifts Dashboard** in Grafana to observe visual plots indicating the extent of model drift.


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


# ADD DRIFTED IMG WITH IMG FOLDER


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

**Previous**: [Experiment Tracking Model Training](../experiment-tracking/experiment-tracking-model-training.md) | **Next**: [Model Observability > Model Observability](../../model-observability/model-observability.md)
