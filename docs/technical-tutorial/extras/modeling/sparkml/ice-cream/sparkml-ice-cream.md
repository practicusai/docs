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

## End-to-end SparkML Model development and deployment 

This sample notebook outlines the process of deploying a SparkML model on the Practicus AI platform and making predictions from the deployed model using various methods.


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
deployment_key = None
prefix = None
model_name = None
practicus_url = None  # E.g. http://company.practicus.com
```

```python
assert deployment_key, "Please select a deployment key"
assert prefix, "Please select a prefix"
assert model_name, "Please enter a model_name"
assert practicus_url, "Please enter practicus_url"
```

```python
import practicuscore as prt

region = prt.current_region()
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

```python
import pandas as pd

# Step 1: Read CSV with Pandas
data = pd.read_csv("/home/ubuntu/samples/data/ice_cream.csv")
```

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.ml.linalg import Vectors

# Step 2: Convert to Spark DataFrame with Explicit Schema
spark = SparkSession.builder.appName("IceCreamRevenuePrediction").getOrCreate()

# Define schema for Spark DataFrame
schema = StructType([StructField("label", DoubleType(), True), StructField("features", DoubleType(), True)])

spark_data = spark.createDataFrame(
    data.apply(lambda row: (float(row["Revenue"]), Vectors.dense(float(row["Temperature"]))), axis=1),
    schema=["label", "features"],
)
```

```python
from pyspark.ml.regression import LinearRegression

# Step 3: Train Linear Regression Model
lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(spark_data)
```

```python
# Step 4: Make Predictions
predictions = model.transform(spark_data)

predictions.select("features", "label", "prediction").show()
```

```python
# Step 5: Save Model
model.save(model_name)
```

```python
# Optional: Stop Spark session when done
spark.stop()
```

```python
# Prediction, you can run this in another notebook

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.ml.regression import LinearRegressionModel


def predict(df: pd.DataFrame) -> pd.DataFrame:
    spark = SparkSession.builder.appName("IceCreamRevenuePrediction").getOrCreate()
    model = LinearRegressionModel.load(model_name)
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

```python
import pandas as pd

data = pd.read_csv("/home/ubuntu/samples/data/ice_cream.csv")
```

```python
prediction = predict(data)

prediction
```

```python
# Optional: Stop Spark session when done
spark.stop()
```

### Deploying the SparkML Model

#### Step 1) Upload to object storage 

- Before you start deploying the model, please upload SparkML model files to the object storage that your Practicus AI model deployment is using.
- Why? Unlike scikit-learn, XGBoost etc., Spark ML model files are not a file such as model.pkl, but a folder. 

##### Sample object storage cache folder

- E.g. s3://my-models-bucket/cache/ice_cream_sparkml_model/ice_cream_sparkml_model/ [ add your model folders here ] 
- Why use same folder name twice? ice_cream_sparkml_model/ice_cream_sparkml_model 
- Practicus AI will download all cache files defined in model.json.
- If you select cache/ice_cream_sparkml_model and don't use the second folder, all of your model files will be downloaded under /var/practicus/cache/
- If you are caching one model only this would work fine, but if you deploy multiple models their files can override each other.

#### Step 2) Verify you Practicus AI model host is SparkML compatible
- Please make sure you are using a Practicus AI model deployment image with SparkML support.
- You can use the default SparkML image: ghcr.io/practicusai/practicus-modelhost-sparkml:{add-version-here}
- Not sure how? Please consult your admin and ask for the deployment key with SparkML.

#### Step 3) Deploy the model
- Please follow the below steps to deploy the model as usual

```python
import practicuscore as prt

# Deploying model as an API
# Please review model.py and model.json files

prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=None,  # Current dir
)
```

```python
region = prt.current_region()

# *All* Practicus AI model APIs follow the below url convention
api_url = f"{region.url}/{prefix}/{model_name}/"
# Important: For effective traffic routing, always terminate the url with / at the end.
print("Model REST API Url:", api_url)
```

```python
token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

```python
# Caution: Due to initial Spark session creation process, first prediction can be quite slow.

import pandas as pd
import requests

df = pd.read_csv("/home/ubuntu/samples/data/ice_cream.csv")

headers = {"authorization": f"Bearer {token}", "content-type": "text/csv"}
data_csv = df.to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df
```


## Supplementary Files

### model.json
```json
{
    "download_files_from": "cache/ice_cream_sparkml_model/",
    "_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### model.py
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


---

**Previous**: [Shap Analysis](../../shap-analysis.md) | **Next**: [Spark For Ds > Spark Tutorial](../spark-for-ds/spark-tutorial.md)
