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
    name: python3
---

### Step 1: Pre-process

##### We will use Practicus SDK to pre process the current data

```python
import practicuscore as prt
import pandas as pd

worker = prt.get_local_worker()
```

```python
conn_conf = {
    "connection_type": "WORKER_FILE",
    "sampling_method": "ALL",
    "file_path": "/home/ubuntu/samples/data/insurance.csv",
}

proc = worker.load(conn_conf)
proc.show_head()
```

```python
df = proc.get_df_copy()
```

### Step 2: Initializing the AutoML Experiment

##### PyCaret's regression module is utilized here for predicting a continuous target variable, i.e., energy costs. We begin by initializing our AutoML experiment.

```python
df_model = df
```

```python
from pycaret.regression import RegressionExperiment, load_model, predict_model

exp = RegressionExperiment()
```

### Step 3: Configuring the Experiment

##### We'll configure our experiment with a specific name, making it easier to manage and reference.

```python
# You need to configure using the service unique key, you can find your key on the "Practicus AI Admin Console"
# service_key = 'mlflow-primary'
# Optionally, you can provide experime name to create a new experiement while configuring
experiment_name = "insurance"

# prt.experiments.configure(service_key=service_key, experiment_name=experiment_name)
# No experiment service selected, will use MlFlow inside the Worker. To configu3re manually:
# prt.experiments.configure(experiment_name=experiment_name, service_name='Experiment service name')
```

### Step 4: Preparing Data with PyCaret's Setup
##### A critical step where we specify our experiment's details, such as the target variable, session ID for reproducibility, and whether to log the experiment for tracking purposes.

```python
# setup_params = {'normalize': True, 'normalize_method': 'minmax',
#'remove_outliers' : True, 'outliers_method':  'iforest'}
```

```python
exp.setup(
    data=df_model,
    target="charges",
    session_id=42,
    log_experiment=True,
    feature_selection=True,
    experiment_name=experiment_name,
)
```

### Step 5: Model Selection and Tuning


##### This command leverages AutoML to compare different models automatically, selecting the one that performs best according to a default or specified metric. It's a quick way to identify a strong baseline model without manual experimentation.

```python
best_model = exp.compare_models(include=["lr", "lasso", "lightgbm"])
```

##### Once a baseline model is selected, this step fine-tunes its hyperparameters to improve performance. The use of tune-sklearn and hyperopt indicates an advanced search across the hyperparameter space for optimal settings, which can significantly enhance model accuracy.


```python
tune_params = {}
```

```python
tuned_model = exp.tune_model(best_model, **tune_params)
```

```python
final_model = exp.finalize_model(tuned_model)
```

```python
predictions = exp.predict_model(final_model, data=df)
display(predictions)
```

```python
predictions
```

```python
exp.save_model(final_model, "model")
```

#### (Recommneded) Adding model metadata to your API
- You can create and upload **model.json** file that defines the input and output schema of your model and potentially other metadata too.
- This will explain how to consume your model efficiently and make it accessible to more users.
- Practicus AI uses MlFlow model input/output standard to define the schema
- You can build the model.json automatically, or let Practicus AI build it for you using the dataframe.

```python
model_config = prt.models.create_model_config(
    df=df,
    target="charges",
    model_name="insurance-4",
    problem_type="Regression",
    version_name="2024-05-30",
    final_model="knn",
    score=4.2493,
)
model_config.save("model.json")
# You also can directly instantiate ModelConfig class to provide more metadata elements
# model_config = prt.models.ModelConfig(...)
```

### Step 6: Model Deployment

```python
df.head()
```

```python
deployment_key = "automl-depl"
prefix = "models"
model_name = "insurance-mlflow-test"
model_dir = None
```

```python
assert deployment_key, "Please select a deployment key"
```

```python
# Deploy to current Practicus AI region
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
    model_dir=model_dir,
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
# We will be using using the SDK to get a session token (or reuse existing, if not expired).
# To learn how to get a token without the SDK, please view 05_others/tokens sample notebook
token = None
token = prt.models.get_session_token(api_url, token=token)
print("API session token:", token)
```

```python
import requests

headers = {"authorization": f"Bearer {token}", "content-type": "text/csv"}
data_csv = df.head(5000).to_csv(index=False)

r = requests.post(api_url, headers=headers, data=data_csv)
if not r.ok:
    raise ConnectionError(f"{r.status_code} - {r.text}")

from io import BytesIO

pred_df = pd.read_csv(BytesIO(r.content))

print("Prediction Result:")
pred_df.head()
```


---

**Previous**: [Generating Wokflows](../AI-Studio/generating-wokflows.md) | **Next**: [Modeling > Introduction](../../modeling/introduction.md)
