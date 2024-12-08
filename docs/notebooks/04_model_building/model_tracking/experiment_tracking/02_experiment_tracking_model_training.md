---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus AutoML
    language: python
    name: practicus_ml
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

```python
service_name = "My Mlflow Service"
# You need to configure using the service unique key, you can find your key on the "Practicus AI Admin Console" 
service_key = ''  
# Optionally, you can provide experime name to create a new experiement while configuring
experiment_name = None
```

```python
prt.experiments.configure(service_name=service_name, service_key=service_key, experiment_name=experiment_name)
```

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
    # Pringting out the run id
    print("Run ID:", mlflow.active_run().info.run_id)
```

```python
# Ending MLFlow
mlflow.end_run()
```


---

**Previous**: [Experiment Tracking Logging](01_experiment_tracking_logging.md) | **Next**: [Model Drift](../model_drifts/Model_Drift.md)
