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

### Locating and getting model access tokens

- In this notebook we will show how to find model prefixes, models and get short lived session tokens.

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

model_prefix = 'models/practicus'
filtered_df = df[(df['prefix'] == model_prefix) & (df['versions'].notna())]
display(filtered_df)
```

```python
model = "diamond-price"

api_url = f"{region.url}/{model_prefix}/{model}/"

print("Geting Model API session token for:", api_url)
token = prt.models.get_session_token(api_url)

print("Model access token with a short life:")
print(token)
```

```python

```

### Getting Model API session token using REST API calls
If your end users do not have access to Practicus AI SDK, they can simply make the below REST API calls with **any programming language** to get a Model API session token.

```python
# "No Practicus SDK" sample to get a session token

import requests

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
r = requests.get(model_api_url + "?get_meta=true", headers=headers, data=data)
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
```

```python

```


## Supplementary Files

### 01_code_quality/bad_code.py
```python
import pandas 

# this is an error
print(undefined_var)




print("Too many blank lines, which is code formatting issue.")

```

### 07_sdk_preprocessing/snippets/impute_missing_knn.py
```python
from enum import Enum


class WeightsEnum(str, Enum):
    uniform = "uniform"
    distance = "distance"


def impute_missing_knn(df, missing_val_col: list[str] | None, n_neighbors: int = 5, weights: WeightsEnum = WeightsEnum.uniform):
    """
    Replaces each missing value using K-Nearest Neighbors technique
    :param missing_val_col: Columns to impute missing values. Leave empty for all columns
    :param n_neighbors: Number of neighboring samples to use for imputation.
    :param weights: Weight function used in prediction
    """
    import pandas as pd
    import numpy as np
    from sklearn.impute import KNNImputer

    knn_imp = KNNImputer(n_neighbors=n_neighbors, weights=str(weights))

    numeric_df = df.select_dtypes(include=[np.number])

    if missing_val_col:
        non_numeric_columns = set(missing_val_col) - set(numeric_df.columns)
        if non_numeric_columns:
            raise ValueError(f"Please only select numeric columns to impute, or do not select any columns. Non-numeric columns: {non_numeric_columns}")

        imputed_data = knn_imp.fit_transform(numeric_df[missing_val_col])
        imputed_df = pd.DataFrame(imputed_data, columns=missing_val_col, index=numeric_df.index)
    else:
        imputed_data = knn_imp.fit_transform(numeric_df)
        imputed_df = pd.DataFrame(imputed_data, columns=numeric_df.columns, index=numeric_df.index)

    df.update(imputed_df)
    return df


impute_missing_knn.worker_required = True
impute_missing_knn.supported_engines = ['pandas']

```

### 07_sdk_preprocessing/snippets/normalize.py
```python
from enum import Enum


class NormalizationOptions(str, Enum):
    Z_SCORE = "Z-Score Normalization"
    MIN_MAX = "Min-Max Normalization"
    ROBUST = "Robust Normalization"


def normalize(df, numeric_col_list: list[str] | None = None, normalization_option: NormalizationOptions = NormalizationOptions.Z_SCORE, result: list[str] | None = None):
    """
    Normalizes certain columns in the DataFrame with the selected normalization method.
    
    :param numeric_col_list: Names of the numeric columns to normalize. If None, all numeric columns are considered.
    :param normalization_option: Specifies the method for normalization: Z-Score (standardizes data), Min-Max (scales data to a fixed range, typically [0, 1]), or Robust (reduces the impact of outliers).
    :param result: Column names to write normalization results. If None, the original column names appended with "_normalized" will be used.
    """
    import numpy as np
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    
    # If no specific columns provided, use all numeric columns
    if numeric_col_list is None:
        numeric_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    # Process according to the selected normalization method
    if normalization_option == NormalizationOptions.Z_SCORE:
        scaler = StandardScaler()
    elif normalization_option == NormalizationOptions.MIN_MAX:
        scaler = MinMaxScaler()
    elif normalization_option == NormalizationOptions.ROBUST:
        scaler = RobustScaler()
    else:
        raise ValueError("Unsupported normalization option selected.")
    
    # Normalize specified columns and assign results either to new columns or overwrite them
    for col in numeric_col_list:
        normalized_col_name = col + "_normalized" if result is None else result.pop(0) if result else f"{col}_normalized"
        df[normalized_col_name] = scaler.fit_transform(df[[col]])

    return df


normalize.worker_required = True
```

### 07_sdk_preprocessing/snippets/suppress_outliers.py
```python
def suppress_outliers(
        df, outlier_float_col_list: list[str] | None, q1_percentile: float = 0.25, q3_percentile: float = 0.75,
        result_col_suffix: str | None = "no_outlier", result_col_prefix: str | None = None):
    """
    Suppresses outliers in specified numeric columns of the dataframe based on custom percentile values for Q1 and Q3.
    Adds new columns with the selected suffix or prefix. If no suffix or prefix is provided, overwrites the existing column.
    :param outlier_float_col_list: List of numeric columns to check for outliers. If left empty, applies to all numeric columns.
    :param q1_percentile: Custom percentile for Q1 (e.g., 0.25 for 25th percentile).
    :param q3_percentile: Custom percentile for Q3 (e.g., 0.75 for 75th percentile).
    :param result_col_suffix: Suffix for the new column where the suppressed data will be stored.
    :param result_col_prefix: Prefix for the new column where the suppressed data will be stored.
    """
    import numpy as np

    # If no specific columns provided, use all numeric columns
    if not outlier_float_col_list:
        outlier_float_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(outlier_float_col_list) == 0:
        raise ValueError("No numeric column provided or located.")

    # Process each specified column
    for col in outlier_float_col_list:
        q1 = df[col].quantile(q1_percentile)
        q3 = df[col].quantile(q3_percentile)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if result_col_suffix:
            new_col_name = f'{col}_{result_col_suffix}'
        elif result_col_prefix:
            new_col_name = f'{result_col_prefix}_{col}'
        else:
            new_col_name = col

        # Create a new column (or override), with suppressed values
        df[new_col_name] = np.where(
            df[col] < lower_bound, lower_bound, np.where(df[col] > upper_bound, upper_bound, df[col])
        )
    
    return df

```

### 08_additional_modeling/bank_marketing/snippets/label_encoder.py
```python
def label_encoder(df, text_col_list: list[str] | None = None):
    """
    Applies label encoding to specified categorical columns or all categorical columns in the dataframe if none are specified.
    :param text_col_list: Optional list of column names to apply label encoding. If None, applies to all categorical columns.
    """
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()

    # If text_col_list is provided, use it; otherwise, select all categorical columns
    if text_col_list is not None:
        categorical_cols = text_col_list
    else:
        categorical_cols = [col for col in df.columns if col.dtype == 'O']

    # Apply Label Encoding to each specified (or detected) categorical column
    for col in categorical_cols:
        # Check if the column exists in the DataFrame to avoid KeyError
        if col in df.columns:
            df[col] = le.fit_transform(df[col])
        else:
            print(f"Warning: Column '{col}' not found in DataFrame.")

    return df


label_encoder.worker_required = True

```

### 08_additional_modeling/bank_marketing/snippets/one_hot.py
```python
from enum import Enum


class DummyOption(str, Enum):
    DROP_FIRST = "Drop First Dummy"
    KEEP_ALL = "Keep All Dummies"


def one_hot(df, text_col_list: list[str] | None,
            max_categories: int = 25, dummy_option: DummyOption = DummyOption.KEEP_ALL,
            result_col_suffix: list[str] | None = None, result_col_prefix: list[str] | None = None):
    """
    Applies one-hot encoding to specified columns in the DataFrame. If no columns are specified,
    one-hot encoding is applied to all categorical columns that have a number of unique categories
    less than or equal to the specified max_categories. It provides an option to either drop the
    first dummy column to avoid multicollinearity or keep all dummy columns.

    :param text_col_list: List of column names to apply one-hot encoding. If None, applies to all
                          suitable categorical columns.
    :param max_categories: Maximum number of unique categories in a column to be included for encoding.
    :param dummy_option: Specifies whether to drop the first dummy column (DROP_FIRST) or keep all
                         (KEEP_ALL).
    :param result_col_suffix: Suffix for the new column where the suppressed data will be stored.
    :param result_col_prefix: Prefix for the new column where the suppressed data will be stored.
    """
    import pandas as pd

    if text_col_list is None:
        text_col_list = [col for col in df.columns if df[col].dtype == 'object' and df[col].nunique() <= max_categories]

    for col in text_col_list:
        dummies = pd.get_dummies(df[col], prefix=(result_col_prefix if result_col_prefix else col),
                                 drop_first=(dummy_option == DummyOption.DROP_FIRST))
        dummies = dummies.rename(columns=lambda x: f'{x}_{result_col_suffix}' if result_col_suffix else x)

        df = pd.concat([df, dummies], axis=1)

    return df

```

### 08_additional_modeling/model_tracking/model_drifts/model.py
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

### 08_additional_modeling/sparkml/model.json
```json
{
    "download_files_from": "cache/ice_cream_sparkml_model/",
    "_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### 08_additional_modeling/sparkml/model.py
```python
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.ml.regression import LinearRegressionModel

spark = None
model = None

# Make sure you downloaded the SparkML model files to the correct cache folder
MODEL_PATH = "/var/practicus/cache/ice_cream_sparkml_model"


async def init(*args, **kwargs):
    global spark, model
    if spark is None:
        spark = SparkSession.builder.appName("IceCreamRevenuePrediction").getOrCreate()
    if model is None:
        model = LinearRegressionModel.load(MODEL_PATH)


async def predict(df: pd.DataFrame | None = None, *args, **kwargs) -> pd.DataFrame:
    # Define schema for Spark DataFrame
    schema = StructType([
        StructField("features", DoubleType(), True)
    ])
    
    # Convert input Pandas DataFrame to Spark DataFrame
    spark_data = spark.createDataFrame(
        df.apply(lambda row: (Vectors.dense(float(row['Temperature'])),), axis=1),
        schema=["features"]
    )
    
    # Make predictions using the Spark model
    predictions = model.transform(spark_data)
    
    # Select the relevant columns and convert to Pandas DataFrame
    predictions_pd = predictions.select("features", "prediction").toPandas()
    
    # Extract the Temperature and predicted Revenue for readability
    predictions_pd["Temperature"] = predictions_pd["features"].apply(lambda x: x[0])
    predictions_pd = predictions_pd.rename(columns={"prediction": "predicted_Revenue"})
    predictions_pd = predictions_pd[["predicted_Revenue"]]
    
    return predictions_pd

```

### 08_additional_modeling/streamlined_model_deployment/model.py
```python
import os
from typing import Optional
import pandas as pd
import numpy as np
from starlette.exceptions import HTTPException
import joblib
 
model_pipeline = None
 
def add_features(df):
    for column in df.select_dtypes(include='object'):
        mode_value = df[column].mode()[0]
        df[column] = df[column].fillna(mode_value)

    for column in df.select_dtypes(include='int64'):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)

    for column in df.select_dtypes(include='float64'):
        mean_value = df[column].mean()
        df[column] = df[column].fillna(mean_value)
    return df
 
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

    # Making predictions
    predictions = model_pipeline.predict(df)
 
    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['income >50K'])
 
    return predictions_df
```

### 08_additional_modeling/xgboost/model.py
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

### 08_additional_modeling/xgboost/model_custom_df.py
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

**Previous**: [Data Catalog](data-catalog.md) | **Next**: [Customizing Templates](customizing-templates.md)
