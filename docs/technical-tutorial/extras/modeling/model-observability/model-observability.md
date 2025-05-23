---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Model Observability and Monitoring

## _Scenario:_ Model Drift

In this example, we'll deploy a model on an income dataset. Our main goal withIn this example is deploying pre-processes into the "model.pkl".

1. _Open_ *Jupyter Notebook*

2. Preparing pre-process function
    
4. Preparing train pipeline and deploy a model on income dataset

5. Making predictions with deployed model without making any pre-process



### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.

```python
deployment_key = None
prefix = None
model_name = None  # Eg. bank_test_1
practicus_url = None  # Eg. http://practicus.company.com
```

```python
assert deployment_key, "Please select a deployment key"
assert prefix, "Please select a prefix"
assert model_name, "Please select a model_name"
assert practicus_url, "Please select practicus_url"
```

```python
import practicuscore as prt

region = prt.get_region()
```

If you don't know your prefixes and deployments you can check them out by using the SDK like down below:

```python
my_model_deployment_list = region.model_deployment_list
display(my_model_deployment_list.to_pandas())
```

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
```

# Creating Preprocess and the Pipeline


Loading the data set

```python
import practicuscore as prt
import pandas as pd

df = pd.read_csv("/home/ubuntu/samples/data/income.csv")

df.head()
```

Creating pre-process function for new features

```python
from sklearn.preprocessing import FunctionTransformer


def add_features(df):
    for column in df.select_dtypes(include="object"):  # Selecting columns which has type as object
        mode_value = df[column].mode()[0]  # Find mode
        df[column] = df[column].fillna(mode_value)

    for column in df.select_dtypes(include="int64"):  # Selecting columns which has type as in64
        mean_value = df[column].mean()  # Find median
        df[column] = df[column].fillna(mean_value)

    for column in df.select_dtypes(include="float64"):  # Selecting columns which has type as float64
        mean_value = df[column].mean()  # Find Median
        df[column] = df[column].fillna(mean_value)

    return df


add_features_transformer = FunctionTransformer(add_features, validate=False)
```

```python
df.columns
```

```python
df.dtypes
```

Defining categorical and numerical features

```python
numeric_features = ["age", "education-num", "capital-gain", "capital-loss", "hours-per-week"]
categorical_features = [
    "workclass",
    "education",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native-country",
]
```

Creating preprocessor object for the pipeline to apply scaling and one hot encoding

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

preprocessor = ColumnTransformer(
    transformers=[("num", StandardScaler(), numeric_features), ("cat", OneHotEncoder(), categorical_features)]
)
```

Creating the pipeline


```python
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

pipeline = Pipeline(
    steps=[
        ("add_features", add_features_transformer),
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier()),
    ]
)
```

# Model Training


Train test split

```python
X = df.drop(["income >50K"], axis=1)
y = df["income >50K"]
```

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

Fitting the model

```python
pipeline.fit(X_train, y_train)
```

```python
score = pipeline.score(X_test, y_test)
print(f"Accuracy Score of the model: {score}")
```

Importing the model by using cloudpickle

```python
import cloudpickle

with open("model.pkl", "wb") as f:
    cloudpickle.dump(pipeline, f)
```

```python
import joblib
import pandas as pd

# Load the saved model
model = joblib.load("model.pkl")

# Making predictions
predictions = model.predict(X)

# Converting predictions to a DataFrame
predictions_df = pd.DataFrame(predictions, columns=["Predictions"])
```

# Deployment of the model

```python
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=None,  # Current dir
)
```

# Prediction

```python
# Let's construct the REST API url.
# Please replace the below url with your current Practicus AI address

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

Making predictions without making any pre-process on the income dataset

```python
import requests

headers = {"authorization": f"Bearer {token}", "content-type": "text/csv"}
data_csv = df.to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```

```python
pred_df.value_counts()
```


## Supplementary Files

### model.py
```python
import os
from typing import Optional
import pandas as pd
import numpy as np
from starlette.exceptions import HTTPException
import joblib

model_pipeline = None


def add_features(df):
    for column in df.select_dtypes(include="object"):
        mode_value = df[column].mode()[0]
        df[column] = df[column].fillna(mode_value)

    for column in df.select_dtypes(include="int64"):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)

    for column in df.select_dtypes(include="float64"):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)
    return df


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, "model.pkl")
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: Optional[pd.DataFrame] = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise HTTPException(status_code=500, detail="No dataframe received")

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=["income >50K"])

    return predictions_df

```


---

**Previous**: [Model Drift](../model-tracking/model-drift/model-drift.md) | **Next**: [XGBoost > XGBoost](../xgboost/xgboost.md)
