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

```python
import practicuscore as prt
import os
import mlflow
import xgboost as xgb
import cloudpickle
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
```

# Experiment Configuration
This code configures the MLflow experiment. It uses the provided `service_name`, `service_key`, and optionally an `experiment_name` to set up the environment for tracking experiments.


```python
# Define the name of the MLflow service for configuration purposes.
service_name = "My Mlflow Service"
# You need to configure using the service unique key, 
# which can be found on the "Practicus AI Admin Console".
service_key = ''  
# Optionally, specify an experiment name to create a new experiment during configuration.
experiment_name = None
```

```python
# Configure the MLflow experiment using the provided service name, service key, 
# and optionally an experiment name. This sets up the environment for tracking experiments.
prt.experiments.configure(service_name=service_name, service_key=service_key, experiment_name=experiment_name)
```

# Load Dataset and Process with Practicus Core
This code snippet demonstrates how to configure and load a dataset in Practicus Core. Here's a step-by-step explanation:
1. Define a dataset connection using a dictionary specifying the connection type (`WORKER_FILE`) and file path to the dataset.
2. Import the Practicus Core library.
3. Retrieve the current region and create or get a worker in that region.
4. Load the dataset connection into the worker.
5. Extract a copy of the dataset as a DataFrame and display the first few rows using the `head()` method.


```python
data_set_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/ice_cream.csv"
}
```

```python
import practicuscore as prt

region = prt.current_region()
worker = region.get_or_create_worker()
proc = worker.load(data_set_conn) 

data = proc.get_df_copy()
data.head()
```

# Experiment Configuration and Data Preparation
This code performs the following tasks:
1. **Set the Experiment Name**: The `mlflow.set_experiment` function assigns a name to the experiment for tracking in MLflow.
2. **Load the Dataset**: Features (`X`) and target (`y`) are extracted from the DataFrame.
3. **Train-Test Split**: The dataset is divided into training and testing sets using an 80-20 split.
4. **Define XGBoost Parameters**: Sets up the hyperparameters for the XGBoost model, including `max_depth`, `eta`, and `objective`.
5. **Create DMatrix**: The `DMatrix` is a data structure optimized for XGBoost, created separately for training and testing sets.


```python
# Set experiment name, if you haven't already while configuring the service
mlflow.set_experiment("XGBoost Experiment")

# Loading the dataset
X = data.Temperature
y = data.Revenue
```

```python
# Test and Train split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
# XGBoost parameters
params = {
    'max_depth': 3,
    'eta': 0.1,
    'objective': 'reg:squarederror',
}
```

```python
# Creation of DMatrix
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)
```

# Model Training, Evaluation, and Logging with MLflow
This code performs the following tasks:
1. **Start an MLflow Run**: Begins a new MLflow run to log parameters, metrics, and artifacts.
2. **Log Parameters**: The XGBoost model parameters are recorded in MLflow for tracking.
3. **Model Training**: The XGBoost model is trained using the specified parameters and training dataset (`dtrain`).
4. **Model Prediction**: Predictions are made on the test dataset (`dtest`).
5. **Evaluate RMSE**: The root mean squared error (RMSE) is calculated to evaluate model performance, and the metric is logged in MLflow.
6. **Save the Model**: 
   - The trained model is serialized and saved as a `.pkl` file locally.
   - The saved model is uploaded to MLflow as an artifact for future reference.
7. **Log Artifacts**: The directory containing the model is logged in MLflow.
8. **Retrieve Run ID**: Outputs the MLflow run ID for reference.
9. **End MLflow Run**: Properly terminates the MLflow run to ensure all data is saved.


```python
# Training of model by using mlflow
with mlflow.start_run():
    mlflow.log_params(params)
    model = xgb.train(params, dtrain, num_boost_round=200)
    # Prediction process
    predictions = model.predict(dtest)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mlflow.log_metric("rmse", rmse)
    # Saving the model in MLFlow
    artifact_path = "model"
    if not os.path.exists(artifact_path):
        os.makedirs(artifact_path)
    model_path = os.path.join(artifact_path, "xgboost_model.pkl")
    with open(model_path, "wb") as f:
        cloudpickle.dump(model, f)
    # Saving the serialised model in MLflow
    mlflow.log_artifacts(artifact_path)
    mlflow.log_artifacts(artifact_path)
    # Printing out the run id
    print("Run ID:", mlflow.active_run().info.run_id)
```

```python
# Ending MLFlow
mlflow.end_run()
```


---

**Previous**: [Experiment Tracking Logging](experiment-tracking-logging.md) | **Next**: [Model Drift > Model Drift](../model-drift/model-drift.md)
