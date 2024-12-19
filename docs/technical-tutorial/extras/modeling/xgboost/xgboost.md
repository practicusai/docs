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

# End-to-End Custom XGBoost Model Development and Deployment

This notebook demonstrates the entire process of developing and deploying a custom XGBoost model on the Practicus AI platform, including making predictions using the deployed model through various methods.

---

## Data Preparation

The data preparation process can be done using Practicus AI for convenience, but manual preparation using libraries like Pandas is also possible. Regardless of the method used, the subsequent steps for model building and deployment remain the same.

### Steps:

1. **Connect to Dataset**:
   - Define the connection to the dataset (`insurance.csv`) using a Practicus Core worker.

2. **Load the Dataset**:
   - Load the dataset into Practicus Core for further processing.

3. **Inspect Initial Data**:
   - Display the first few rows of the dataset using `proc.show_head()`.

4. **Perform Categorical Mapping**:
   - Convert categorical columns (`sex`, `smoker`, and `region`) into separate categorical representations with the suffix `category`.

5. **Delete Unnecessary Columns**:
   - Remove the original categorical columns (`region`, `smoker`, `sex`) after mapping to avoid redundancy.

6. **Retrieve Data as Pandas DataFrame**:
   - Export the processed dataset to a Pandas DataFrame for further steps, such as model training.

---

### Code for Data Preparation


```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/insurance.csv"
}
```

```python
import practicuscore as prt

region = prt.current_region()
worker = region.get_or_create_worker()
proc = worker.load(data_set_conn) 

proc.show_head()
```

```python
proc.categorical_map(column_name='sex', column_suffix='category') 
proc.categorical_map(column_name='smoker', column_suffix='category') 
proc.categorical_map(column_name='region', column_suffix='category') 
proc.delete_columns(['region', 'smoker', 'sex']) 
```

```python
df = proc.get_df_copy()
df.head()
```

## Building the Model

This section demonstrates how to build a regression model using XGBoost to predict insurance charges. The steps involve splitting the data into training and testing sets, creating a pipeline with XGBoost, and training the model.

---

### Steps:

1. **Feature-Target Split**:
   - Separate the features (`X`) from the target variable (`y`), where:
     - `X` contains all columns except `charges`.
     - `y` contains the `charges` column, which is the target variable.

2. **Train-Test Split**:
   - Split the data into training and testing sets using an 80-20 ratio.
   - Set a random seed (`random_state=42`) for reproducibility.

3. **Model Creation**:
   - Use `Pipeline` from `sklearn` to encapsulate the machine learning workflow.
   - Add an `XGBRegressor` to the pipeline, configured with:
     - `objective`: Set to `'reg:squarederror'` for regression tasks.
     - `n_estimators`: Number of trees to build.

4. **Model Training**:
   - Fit the pipeline to the training data (`X_train`, `y_train`).

---

### Code for Model Building


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

## Saving and Using the Model

Once the model is trained, it can be saved and reused for making predictions. The steps below outline the process:

---

### Steps:

1. **Save the Model**:
   - Use `cloudpickle` to save the trained pipeline as a `.pkl` file. 
   - Saving with `cloudpickle` ensures that custom components (like preprocessing steps) in the pipeline remain portable.

2. **Load the Saved Model**:
   - Use `joblib` to load the saved model back into memory.

3. **Make Predictions**:
   - Use the loaded model to make predictions on the feature set (`X`).
   - Store the predictions in a Pandas DataFrame for easy viewing and analysis.

---

### Code for Saving and Using the Model


```python
import cloudpickle

with open('model.pkl', 'wb') as f:
    cloudpickle.dump(pipeline, f)
```

```python
import joblib 
import pandas as pd

# Load the saved model
model = joblib.load('model.pkl')

# Making predictions
predictions = model.predict(X)

pred_df = pd.DataFrame(predictions, columns=['Predictions'])
pred_df.head()
```

## Kubernetes Model Deployment with Practicus AI

This section demonstrates how to locate and prepare a Kubernetes deployment for deploying your trained XGBoost model. It also provides a link to create a `model.py` file, which contains the logic for making predictions using the deployed model.

---

### Steps:

1. **Locate Kubernetes Deployment**:
   - Check if there are available Kubernetes model deployment systems in the current region.
   - Raise an error if no deployment system is found.
   - If multiple deployments are available, use the first one.

2. **Set Deployment Parameters**:
   - `deployment_key`: The unique key identifying the Kubernetes deployment.
   - `prefix`: A string prefix for organizing the deployment (`models`).
   - `model_name`: The name to assign to the deployed model (`my-xgboost-model`).
   - `model_dir`: Optionally specify the directory of the model. If `None`, the current directory is used.

3. **Prepare for Deployment**:
   - Prints the deployment configuration, indicating where the model will be deployed.

4. **Create `model.py`**:
   - A `model.py` file should contain the logic for loading `model.pkl` and predicting based on incoming requests.
   - Refer to the provided link to view a sample implementation.

---

### Code for Kubernetes Model Deployment


```python
# Let's locate the Kubernetes model deployment to deploy our model
if len(region.model_deployment_list) == 0:
    raise SystemError("You do not have any model deployment systems. "
                      "Please contact your system admin.")
elif len(region.model_deployment_list) > 1:
    print("You have more than one model deployment systems. "
          "Will use the first one")
model_deployment = region.model_deployment_list[0]
deployment_key = model_deployment.key
prefix = 'models'
model_name = 'my-xgboost-model'
model_dir = None  # Current dir

print(f"Will deploy '{prefix}/{model_name}' to '{deployment_key}' kubernetes deployment")
```

#### Create model.py that predicts using model.pkl

[View sample model.py code](model.py)


## Deploying the Model and Generating API Details

This section outlines how to deploy the trained model to a Kubernetes system using Practicus AI, retrieve the API URL, and generate a session token for secure interaction with the deployed model.

---

### Steps:

1. **Deploy the Model**:
   - Use `prt.models.deploy()` to deploy the model to the specified Kubernetes deployment.
   - Deployment parameters include:
     - `deployment_key`: The unique key for the Kubernetes deployment.
     - `prefix`: A prefix for organizing the deployment.
     - `model_name`: The name of the model.
     - `model_dir`: Directory of the model files (default is the current directory).

2. **Construct the API URL**:
   - After deployment, construct the REST API URL for the deployed model.
   - The API URL follows the convention: `{region.url}/{prefix}/{model_name}/`.
   - Ensure the URL ends with a `/` for effective traffic routing.

3. **Generate API Session Token**:
   - Use `prt.models.get_session_token()` to retrieve a secure session token for the API.
   - This token is required for authorized access to the model's REST API.

4. **Print API Details**:
   - Display the constructed API URL and the generated session token for reference.

---

### Code for Deployment and API Configuration


```python
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir
)
```

#### Making predictions using the model API

```python
# *All* Practicus AI model APIs follow the below url convention
api_url = f"{region.url}/{prefix}/{model_name}/"
# Important: For effective traffic routing, always terminate the url with / at the end.
print("Model REST API Url:", api_url)
```

#### Getting a session token for the model API
- You can programmatically get a short-lived (~4 hours) model session token (recommended)
- You can also get an access token that your admin provided with a custom life span, e.g. months.

```python
# We will be using using the SDK to get a session token.
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

#### Posting data

- There are multiple ways to post your data and construct the DataFrame in your model.py code.
- If you add **content-type** header, Practicus AI model hosting system will automatically convert your csv data into a Pandas DataFrame, and pass on to model.py predict() method.
- If you would like to construct the Dataframe yourself, skip passing content-type header and construct using Starlette request object [View sample code](model_custom_df.py)

```python
import requests 

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

#### Compressing API traffic
- Practicus AI currently supports 'lz4' (recommended), 'zlib', 'deflate' and 'gzip' compression algorithms.
- Compressing to and from the API endpoint can increase performance for large datasets, low network bandwidth.

```python
import lz4 

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'text/csv',
    'content-encoding': 'lz4'
}
data_csv = X.to_csv(index=False)
compressed = lz4.frame.compress(data_csv.encode())
print(f"Request compressed from {len(data_csv)} bytes to {len(compressed)} bytes")

r = requests.post(api_url, headers=headers, data=compressed)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

decompressed = lz4.frame.decompress(r.content)
print(f"Response de-compressed from {len(r.content)} bytes to {len(decompressed)} bytes")

pred_df = pd.read_csv(BytesIO(decompressed))

print("Prediction Result:")
pred_df.head()
```

#### Detecting drift

If enabled, Practicus AI allows you to detect feature and prediction drift and visualize in an observability platform such as Grafana. 

```python
# Let's create an artificial drift for BMI feature, which will also affect charges
df["bmi"] = df["bmi"] * 1.2

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

#### (Recommended) Adding model metadata to your API
- You can create and upload **model.json** file that defines the input and output schema of your model and potentially other metadata too.
- This will explain how to consume your model efficiently and make it accessible to more users.
- Practicus AI uses MlFlow model input/output standard to define the schema
- You can build the model.json automatically, or let Practicus AI build it for you using the dataframe.

```python
model_config = prt.models.create_model_config(
    df=df,
    target="charges",
    model_name="My XG Boost Model",
    problem_type="Regression",
    version_name="2024-02-15",
    final_model="xgboost",
    score=123
)
model_config.save("model.json")
# You also can directly instantiate ModelConfig class to provide more metadata elements
# model_config = prt.models.ModelConfig(...)
```

#### Adding a new API version
- You can add as many model version as you need.
- Your admin can then route traffic as needed, Including for A/B testing.

```python
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir
)
```

#### Reading model metadata

You can add the query string '?get_meta=true' to any model to get the metadata.

```python
headers = {'authorization': f'Bearer {token}'}
r = requests.get(api_url + '?get_meta=true', headers=headers)

if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

import json
from pprint import pprint

model_config_dict = json.loads(r.text)
print("Model metadata:")
pprint(model_config_dict)
schema_dict = json.loads(model_config_dict["model_signature_json"])
print("Model input/output schema:")
pprint(schema_dict)
```

### (Optional) Consuming custom model APIs from Practicus AI App

Practicus AI App users can consume any REST API model. 

#### End user API view

If you add metadata to your models, App users will be able to view your model details in the UI.

#### Feature matching

If your model has an input/output schema, the App will try to match them to current dataset.

#### Viewing the prediction result

Note: Please consider adding categorical mapping to your models as a pre-processing step for improved user experience.


##### (Recommended) Clean-up
Explicitly calling kill() on your processes will free un-used resources on your worker faster.

```python
proc.kill()
```


## Supplementary Files

### model.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: pd.DataFrame | None = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise ValueError("No dataframe received")

    if 'charges' in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop('charges', axis=1)

        # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predictions'])

    return predictions_df

```

### model_custom_df.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'model.pkl')
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, *args, **kwargs) -> pd.DataFrame:
    # Add the code that creates a dataframe using Starlette Request object http_request
    # E.g. read bytes using http_request.stream(), decode and pass to Pandas.
    raise NotImplemented("DataFrame generation code not implemented")

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

**Previous**: [Model Observability](../model-observability/model-observability.md) | **Next**: [AutoML](../AutoML.md)
