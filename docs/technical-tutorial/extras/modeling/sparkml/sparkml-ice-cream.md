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

# End-to-end SparkML Model development and deployment 

This sample notebook outlines the process of deploying a SparkML model on the Practicus AI platform and making predictions from the deployed model using various methods.


## Converting Pandas DataFrame to Spark DataFrame with Explicit Schema
This code performs the following tasks:
1. **Read CSV with Pandas**:
   - Reads a CSV file (`ice_cream.csv`) containing data into a Pandas DataFrame for initial processing.
2. **Initialize Spark Session**:
   - Creates a Spark session named "IceCreamRevenuePrediction" to enable distributed data processing.
3. **Define Explicit Schema**:
   - Creates a schema for the Spark DataFrame with two fields:
     - `label`: A `DoubleType` field representing the target variable (`Revenue`).
     - `features`: A `DoubleType` field containing feature vectors.
4. **Convert Pandas DataFrame to Spark DataFrame**:
   - Applies a transformation to convert each row of the Pandas DataFrame into a tuple containing the label and feature vector.
   - Uses the defined schema to create a Spark DataFrame for further processing.


```python
import pandas as pd

# Step 1: Read CSV with Pandas
data = pd.read_csv("/home/ubuntu/samples/ice_cream.csv")
```

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DoubleType
from pyspark.ml.linalg import Vectors

# Step 2: Convert to Spark DataFrame with Explicit Schema
spark = SparkSession.builder.appName("IceCreamRevenuePrediction").getOrCreate()

# Define schema for Spark DataFrame
schema = StructType([
    StructField("label", DoubleType(), True),
    StructField("features", DoubleType(), True)
])

spark_data = spark.createDataFrame(
    data.apply(lambda row: (float(row['Revenue']), Vectors.dense(float(row['Temperature']))), axis=1),
    schema=["label", "features"]
)
```

# Training and Saving a Spark ML Linear Regression Model
This code demonstrates the following steps:
1. **Train Linear Regression Model**:
   - Initializes a `LinearRegression` model from Spark MLlib, specifying `featuresCol` and `labelCol`.
   - Fits the model to the prepared Spark DataFrame (`spark_data`).
2. **Make Predictions**:
   - Uses the trained model to predict the target variable (`Revenue`) based on the features (`Temperature`).
   - Displays the features, actual labels, and predictions in a Spark DataFrame.
3. **Save Model**:
   - Saves the trained model to disk using the specified `model_name` (`ice_cream_sparkml_model`) for reuse.
4. **Stop Spark Session**:
   - Optionally stops the Spark session to free resources after completing the tasks.


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
model_name = "ice_cream_sparkml_model"
model.save(model_name)
```

```python
# Optional: Stop Spark session when done
spark.stop()
```

# Predicting Revenue Using a Saved Spark ML Model
This function allows you to load a pre-trained Spark ML model and make predictions on new data:
1. **Spark Session Initialization**:
   - Creates a Spark session to enable Spark ML operations.
2. **Load the Saved Model**:
   - Loads the `LinearRegressionModel` previously saved using the specified `model_name`.
3. **Input Schema Definition**:
   - Defines a schema for the Spark DataFrame, containing a single column `features` of type `DoubleType`.
4. **Convert Pandas DataFrame to Spark DataFrame**:
   - Converts the input Pandas DataFrame (`df`) into a Spark DataFrame compatible with the model.
   - The `Temperature` column is transformed into feature vectors using `Vectors.dense`.
5. **Make Predictions**:
   - Passes the Spark DataFrame through the model to generate predictions.
   - The output Spark DataFrame includes `features` and `prediction` columns.
6. **Format Predictions**:
   - Converts the Spark DataFrame back to a Pandas DataFrame for easier handling.
   - Extracts and formats the `Temperature` and `predicted_Revenue` columns for a user-friendly output.
7. **Return Results**:
   - The resulting Pandas DataFrame contains the predicted revenue for the provided temperature values.


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

```python
import pandas as pd

data = pd.read_csv("/home/ubuntu/samples/ice_cream.csv")
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

deployment_key = "sparkml"  # must point to a SparkML compatible model host
prefix = "models"
model_name = "ice-cream-sparkml"
model_dir = None  # Current dir

prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir    
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

# Making Predictions with Deployed Model via REST API
This code illustrates how to send data to a deployed model's REST API for predictions and retrieve the results:
1. **Dataset Loading**:
   - Reads the dataset from a CSV file (`ice_cream.csv`) into a Pandas DataFrame.
2. **Set Up API Request**:
   - Defines HTTP headers, including:
     - Authorization token (`Bearer {token}`) for access.
     - Content type as `text/csv`.
   - Converts the DataFrame to CSV format for compatibility with the API.
3. **Send Data to REST API**:
   - Makes a `POST` request to the deployed model's REST API endpoint (`api_url`), passing the data and headers.
   - Raises a `ConnectionError` if the request fails.
4. **Process API Response**:
   - Reads the response content from the API and converts it into a Pandas DataFrame.
5. **Display Prediction Results**:
   - Outputs the prediction results as a Pandas DataFrame for review.
6. **Note on Performance**:
   - The initial prediction may be slower due to the Spark session startup process, especially if it's not yet initialized.


```python
# Caution: Due to initial Spark session creation process, first prediction can be quite slow.

import pandas as pd
import requests 

df = pd.read_csv("/home/ubuntu/samples/ice_cream.csv")

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


---

**Previous**: [Spark Object Storage](../../data-processing/process-data/spark-object-storage.md) | **Next**: [Model Tracking > Experiment Tracking > Experiment Tracking Logging](../model-tracking/experiment-tracking/experiment-tracking-logging.md)
