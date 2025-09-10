---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: practicus
---

# Distributed XGBoost with Dask for Scalable Machine Learning

This example showcases the use of Dask for distributed computing with XGBoost, enabling efficient training on large datasets. We cover:

*   Training an XGBoost model on a Dask cluster.
*   Saving the trained model to disk.
*   Loading the saved model and making predictions on new data.

```python
worker_size = None
worker_count = None
model_path = "model.ubj"
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert model_path, "Please enter your model_path."
```

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
        job_type=prt.DistJobType.dask,
        worker_count=worker_count,
    )
    worker_config = prt.WorkerConfig(
        worker_size=worker_size,
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
# Check most recent docs:
# https://xgboost.readthedocs.io/en/stable/tutorials/dask.html

from xgboost import dask as dxgb

import dask.array as da
import dask.distributed

num_obs = 1e5
num_features = 20
X = da.random.random(size=(num_obs, num_features), chunks=(1000, num_features))
y = da.random.random(size=(num_obs, 1), chunks=(1000, 1))

dtrain = dxgb.DaskDMatrix(client, X, y)
# or
# dtrain = dxgb.DaskQuantileDMatrix(client, X, y)

output = dxgb.train(
    client,
    {"verbosity": 2, "tree_method": "hist", "objective": "reg:squarederror"},
    dtrain,
    num_boost_round=4,
    evals=[(dtrain, "train")],
)
print("Model trained successfully")

prediction = dxgb.predict(client, output, X)
print("Predictions made successfully")

prediction = dxgb.inplace_predict(client, output, X)
print("Predictions made successfully using inplace version")

output["booster"].save_model(model_path)
print(f"Model saved to {model_path}")
```

### Load and train with the XGBoost model

```python
import xgboost as xgb

print("Loading Model and Predicting")

# Load the saved model
loaded_bst = xgb.Booster()
loaded_bst.load_model(model_path)
print("Model loaded successfully")

# Generate a *new* random dataset (important: different from training/testing)
X_new = da.random.random(size=(num_obs, num_features), chunks=(1000, num_features))  # New data!
X_new_computed = client.compute(X_new).result()  # Important to compute before creating DMatrix
dnew = xgb.DMatrix(X_new_computed)

# Make predictions using the loaded model
new_preds = loaded_bst.predict(dnew)
print("New predictions made successfully")

# Print some predictions (convert to NumPy array for easier printing)
print("First 10 New Predictions:")
print(new_preds[:10])
```

### Deploying model as an API

Note: If you would like to deploy the XGBoost model as an API, please visit the modeling basics section.

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
