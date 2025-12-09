---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus_ml
    language: python
    name: python3
---

# Predicting Insurance Charges with Automated Machine Learning (AutoML)

In the insurance sector, accurately forecasting the costs associated with policyholders is crucial for pricing policies competitively while ensuring profitability. For insurance companies, the ability to predict these costs helps in tailoring individual policies, identifying key drivers of insurance costs, and ultimately enhancing customer satisfaction by offering policies that reflect a customer's specific risk profile and needs.

### Objective

The primary goal of this notebook is to showcase how Practicus AI users can leverage AutoML to swiftly and proficiently develop a predictive model, minimizing the need for extensive manual modeling work. By engaging with this notebook, you'll acquire knowledge on how to:

- Load the dataset specific to insurance costs

- Using AutoML to train and tune a predictive model tailored for insurance charges prediction.

- Assess the model's performance accurately

Let's embark on this journey!


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
service_key = None  # Eg. Mlflow
experiment_name = None  # Eg. automl-experiment-test
```

```python
assert service_key, "Please select a service_key"
assert experiment_name, "Please select a experiment_name"
```

```python
import practicuscore as prt

region = prt.current_region()
```

```python
# If you don't know experiment service key and name you can checkout down below

addon_list = prt.addons.get_list()
display(addon_list.to_pandas())
```

<!-- #region -->
### Step 1: Setting Up the Environment


##### First, we need to set up our Python environment with the necessary libraries. PyCaret, an AutoML library, simplifies the machine learning workflow, enabling us to efficiently develop predictive models.

<!-- #endregion -->

```python
# Standard libraries for data manipulation and numerical operations
import pandas as pd
import numpy as np
from pycaret.regression import *  # Importing PyCaret's regression module

# Extras
import warnings

warnings.filterwarnings("ignore")
```

### Step 2: Loading the Dataset


##### The dataset consists of 1,337 observations and 7 variables, with 'charges' being the target variable we aim to predict. This dataset is a common benchmark in insurance cost predictions.

```python
data_set_conn = {"connection_type": "WORKER_FILE", "file_path": "/home/ubuntu/samples/data/insurance.csv"}
```

```python
import practicuscore as prt

worker = prt.get_local_worker()

proc = worker.load(data_set_conn, engine="AUTO")

df = proc.get_df_copy()
display(df)
```

### Step 3: Initializing the AutoML Experiment

##### PyCaret's regression module is utilized here for predicting a continuous target variable, i.e., insurance costs. We begin by initializing our AutoML experiment.

```python
from pycaret.regression import RegressionExperiment, load_model, predict_model

exp = RegressionExperiment()
```

##### This step sets up our environment within PyCaret, allowing for automated feature engineering, model selection, and more.


### Step 4: Configuring the Experiment

##### We'll configure our experiment with a specific name, making it easier to manage and reference.

```python
prt.experiments.configure(service_key=service_key, experiment_name=experiment_name)
# No experiment service selected, will use MlFlow inside the Worker. To configure manually:
# configure_experiment(experiment_name=experiment_name, service_name='Experiment service name')
```

### Step 5: Preparing Data with PyCaret's Setup
##### A critical step where we specify our experiment's details, such as the target variable, session ID for reproducibility, and whether to log the experiment for tracking purposes.

```python
setup_params = {"normalize": True, "normalize_method": "minmax"}
```

```python
exp.setup(
    data=df,
    target="charges",
    session_id=42,
    log_experiment=True,
    feature_selection=True,
    experiment_name=experiment_name,
    **setup_params,
)
```

### Step 6: Model Selection and Tuning


##### This command leverages AutoML to compare different models automatically, selecting the one that performs best according to a default or specified metric. It's a quick way to identify a strong baseline model without manual experimentation.

```python
best_model = exp.compare_models()
```

##### Once a baseline model is selected, this step fine-tunes its hyperparameters to improve performance. The use of tune-sklearn and hyperopt indicates an advanced search across the hyperparameter space for optimal settings, which can significantly enhance model accuracy.


```python
tune_params = {}
```

```python
tuned_model = exp.tune_model(best_model, **tune_params)
```

### Step 7: Finalizing the Model



##### After tuning, the model is finalized, meaning it's retrained on the entire dataset, including the validation set. This step ensures the model is as generalized as possible before deployment.

```python
final_model = exp.finalize_model(tuned_model)
```

```python
proc.kill()
```

### Step 8: Predictions and Saving the Model



##### We predict insurance costs using our final model and save it for future use, ensuring operational scalability.

```python
predictions = exp.predict_model(final_model, data=df)
display(predictions)
```

##### The last step involves saving the trained model for future use, such as deployment in a production environment or further evaluation. It ensures the model's availability beyond the current session, facilitating operationalization and scalability.

```python
exp.save_model(final_model, "model")
```

```python
loaded_model = load_model("model")

predictions = predict_model(loaded_model, data=df)
display(predictions)
```

<!-- #region -->
# Summary


##### By following these steps, insurance companies can develop a predictive model for insurance costs using Practicus AI's AutoML capabilities. This approach reduces the need for extensive manual modeling, enabling insurers to efficiently adapt to changing market conditions and customer profiles.
<!-- #endregion -->


## Supplementary Files

### examples/bank_marketing/snippets/label_encoder.py
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
        categorical_cols = [col for col in df.columns if col.dtype == "O"]

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

### examples/bank_marketing/snippets/one_hot.py
```python
from enum import Enum


class DummyOption(str, Enum):
    DROP_FIRST = "Drop First Dummy"
    KEEP_ALL = "Keep All Dummies"


def one_hot(
    df,
    text_col_list: list[str] | None,
    max_categories: int = 25,
    dummy_option: DummyOption = DummyOption.KEEP_ALL,
    result_col_suffix: list[str] | None = None,
    result_col_prefix: list[str] | None = None,
):
    """
    Applies one-hot encoding to specified columns in the DataFrame. If no columns are specified,
    one-hot encoding is applied to all categorical columns that have a number of unique categories
    less than or equal to the specified max_categories. It provides an option to either drop the
    first dummy column to avoid multi collinearity or keep all dummy columns.

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
        text_col_list = [col for col in df.columns if df[col].dtype == "object" and df[col].nunique() <= max_categories]

    for col in text_col_list:
        dummies = pd.get_dummies(
            df[col],
            prefix=(result_col_prefix if result_col_prefix else col),
            drop_first=(dummy_option == DummyOption.DROP_FIRST),
        )
        dummies = dummies.rename(columns=lambda x: f"{x}_{result_col_suffix}" if result_col_suffix else x)

        df = pd.concat([df, dummies], axis=1)

    return df

```

### model_observability/model.py
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

### model_tracking/model_drift/model.py
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
    model_file = os.path.join(current_dir, "model.pkl")
    if not os.path.exists(model_file):
        raise HTTPException(status_code=404, detail=f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: Optional[pd.DataFrame] = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise HTTPException(status_code=500, detail="No dataframe received")

    if "charges" in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop("charges", axis=1)

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=["Predictions"])

    return predictions_df

```

### sparkml/ice_cream/model.json
```json
{
    "download_files_from": "cache/ice_cream_sparkml_model/",
    "_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### sparkml/ice_cream/model.py
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
    schema = StructType([StructField("features", DoubleType(), True)])

    # Convert input Pandas DataFrame to Spark DataFrame
    spark_data = spark.createDataFrame(
        df.apply(lambda row: (Vectors.dense(float(row["Temperature"])),), axis=1), schema=["features"]
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

### sparkml/spark_with_job/job.py
```python
import practicuscore as prt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit, max, min, stddev, corr
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml import Pipeline

spark = SparkSession.builder.appName("Advanced Data Processing").getOrCreate()

file_path = "/home/ubuntu/samples/data/insurance.csv"
data = spark.read.csv(file_path, header=True, inferSchema=True)
missing_data = data.select([count(when(col(c).isNull(), c)).alias(c) for c in data.columns])

categorical_columns = ["sex", "smoker", "region"]
indexers = [StringIndexer(inputCol=col, outputCol=col + "_index") for col in categorical_columns]
encoders = [OneHotEncoder(inputCol=col + "_index", outputCol=col + "_encoded") for col in categorical_columns]

data = data.withColumn(
    "bmi_category",
    when(col("bmi") < 18.5, lit("underweight"))
    .when((col("bmi") >= 18.5) & (col("bmi") < 25), lit("normal"))
    .when((col("bmi") >= 25) & (col("bmi") < 30), lit("overweight"))
    .otherwise(lit("obese")),
)

feature_columns = ["age", "bmi", "children", "sex_encoded", "smoker_encoded", "region_encoded"]
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=False)

pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler])
data = pipeline.fit(data).transform(data)

output_path = "/home/ubuntu/my/processed_insurance_data.parquet/"

data.write.parquet(output_path, mode="overwrite")

spark.stop()

```

### sparkml/spark_with_job/run/2c741e/prt_dist_job.json
```json
{"job_type":"spark","job_dir":"~/my/02_batch_job/","initial_count":2,"coordinator_port":7077,"additional_ports":[4040,7078,7079],"terminate_on_completion":false,"py_file":"job.py","executors":[{"rank":0,"instance_id":"5cf16b71"},{"rank":1,"instance_id":"63e80dc8"}]}
```

### sparkml/spark_with_job/run/2c741e/rank_0.json
```json
{"rank":0,"instance_id":"5cf16b71","state":"completed","used_ram":1187,"peak_ram":1187,"total_ram":3200,"gpus":0,"used_vram":0,"peak_vram":0,"reserved_vram":0,"total_vram":0}
```

### sparkml/spark_with_job/run/2c741e/rank_1.json
```json
{"rank":1,"instance_id":"63e80dc8","state":"running","used_ram":284,"peak_ram":293,"total_ram":3200,"gpus":0,"used_vram":0,"peak_vram":0,"reserved_vram":0,"total_vram":0}
```

### xgboost/model.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, "model.pkl")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, df: pd.DataFrame | None = None, *args, **kwargs) -> pd.DataFrame:
    if df is None:
        raise ValueError("No dataframe received")

    if "charges" in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop("charges", axis=1)

        # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=["Predictions"])

    return predictions_df

```

### xgboost/model_custom_df.py
```python
import os
import pandas as pd
import joblib

model_pipeline = None


async def init(model_meta=None, *args, **kwargs):
    global model_pipeline

    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, "model.pkl")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Could not locate model file: {model_file}")

    model_pipeline = joblib.load(model_file)


async def predict(http_request, *args, **kwargs) -> pd.DataFrame:
    # Add the code that creates a dataframe using Starlette Request object http_request
    # E.g. read bytes using http_request.stream(), decode and pass to Pandas.
    raise NotImplemented("DataFrame generation code not implemented")

    if "charges" in df.columns:
        # Dropping 'charges' since it is the target
        df = df.drop("charges", axis=1)

    # Making predictions
    predictions = model_pipeline.predict(df)

    # Converting predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=["Predictions"])

    return predictions_df

```


---

**Previous**: [Work With Processes](../../how-to/work-with-processes.md) | **Next**: [Data Mining > Pattern Mining](data-mining/pattern-mining.md)
