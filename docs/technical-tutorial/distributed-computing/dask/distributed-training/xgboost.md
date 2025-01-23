---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Distributed XGBoost with Dask for Scalable Machine Learning

This example showcases the use of Dask for distributed computing with XGBoost, enabling efficient training on large datasets. We cover:

*   Training an XGBoost model on a Dask cluster.
*   Saving the trained model to disk.
*   Loading the saved model and making predictions on new data.

```python
import practicuscore as prt

# Let's start with creating an interactive Dask cluster 
# Note: you can also run this as a batch job.
# To learn more, please view the batch section of this guide.

if prt.distributed.running_on_a_cluster():
    print("You are already running this code on a distributed cluster. No need to create a new one..")
else:
    print("Starting a new distributed Dask cluster.")
    distributed_config = prt.DistJobConfig(
        job_type = prt.DistJobType.dask,
        worker_count = 2,
    )
    worker_config = prt.WorkerConfig(
        worker_size="X-Small",
        distributed_config=distributed_config,
    )
    coordinator_worker = prt.create_worker(
        worker_config=worker_config,
    )
    
    # Let's login to the cluster coordinator
    notebook_url = coordinator_worker.open_notebook()
    
    print("Page did not open? You can open this url manually:", notebook_url)
```

### Execute on Dask Cluster

- If you just created a new cluster, please open the new browser tab to login to the Distributed Dask coordinator, and continue with the below steps..
- If you are already on the cluster, you can continue with the below steps..


#### (Optional) Viewing training details on the Dask dashboard

If you would like to view training details, please login the Dask dashboard with the below.

```python
import practicuscore as prt

dashboard_url = prt.distributed.open_dashboard()

print("Page did not open? You can open this url manually:", dashboard_url)
```

```python
import practicuscore as prt 

# Let's get a Dask session
client = prt.distributed.get_client()
```

#### Training with XGBoost on Dask Cluster

```python
import xgboost as xgb
import dask.array as da
from dask_ml.model_selection import train_test_split
import numpy as np
import dask.distributed

# Generate some random data (replace with your actual data)
X = da.random.random((1000, 10), chunks=(100, 10))
y = da.random.randint(0, 2, size=1000, chunks=100)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Convert Dask arrays to DaskDMatrix (XGBoost-compatible format)
dtrain = xgb.dask.DaskDMatrix(client, X_train, y_train)
dtest = xgb.dask.DaskDMatrix(client, X_test, y_test)

# Set XGBoost parameters
params = {
    'objective': 'binary:logistic',
    'max_depth': 6,
    'eta': 0.3,
    'tree_method': 'hist'
}

# Train the model
bst = xgb.dask.train(client, params, dtrain, num_boost_round=100)
print("Model trained successfully")

# Optionally, evaluate the model on test data
preds = xgb.dask.predict(client, bst, dtest)
print("Predictions made successfully")

model_path = "model.ubj"
bst['booster'].save_model(model_path)
print(f"Model saved to {model_path}")
```

### Deploying model as an API

Note: If you would like to deploy the XGBoost model as an API, please visit the modeling basics section.


### Load and train with the XGBoost model

```python
print("Loading Model and Predicting")

# Load the saved model
loaded_bst = xgb.Booster()
loaded_bst.load_model(model_path)
print("Model loaded successfully")

# Generate a *new* random dataset (important: different from training/testing)
X_new = da.random.random((500, 10), chunks=(100, 10))  # New data!
X_new_computed = client.compute(X_new).result() # Important to compute before creating DMatrix
dnew = xgb.DMatrix(X_new_computed)

# Make predictions using the loaded model
new_preds = loaded_bst.predict(dnew)
print("New predictions made successfully")

# Print some predictions (convert to NumPy array for easier printing)
print("First 10 New Predictions:")
print(new_preds[:10])
```

```python
# Cleanup
try:
    # if code is running where you started the cluster
    coordinator_worker.terminate()
except:
    # Or else, let's terminate self, which will also terminate the cluster.
    prt.get_local_worker().terminate()
```


---

**Previous**: [Batch Job](../batch-job/batch-job.md) | **Next**: [DeepSpeed > Basics > Intro To DeepSpeed](../../deepspeed/basics/intro-to-deepspeed.md)
