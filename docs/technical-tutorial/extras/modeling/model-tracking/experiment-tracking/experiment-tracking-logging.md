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

```python
import practicuscore as prt
import os
import mlflow

region = prt.current_region()
```

```python
# Defining parameters

# You need to configure using the service unique key and name
service_name = None
service_key = None

# Optionally, you can provide experiment name to create a new experiment while configuring
experiment_name = None
```

```python
assert service_name, "Please select a service_name"
assert service_key, "Please select a service_key"
assert experiment_name, "Please enter a experiment_name"
```

```python
# If you don't know service key and name you can checkout down below

addon_list = prt.addons.get_list()
display(addon_list.to_pandas())
```

```python
prt.experiments.configure(service_name=service_name, service_key=service_key, experiment_name=experiment_name)
```

```python
# Set experiment name, if you haven't already while configuring the service
mlflow.set_experiment("my experiment")

# Prefer unique run names, or leave empty to auto generate unique names
run_name = "My ML experiment run 123"

# Start an MLflow run and log params, metrics and artifacts
with mlflow.start_run(run_name=run_name):
    # Log parameters
    mlflow.log_param("param1", 5)
    mlflow.log_param("param2", "test")

    # Log metrics
    mlflow.log_metric("metric1", 0.85)

    # Create an artifact (e.g., a text file)
    artifact_path = "artifacts"
    if not os.path.exists(artifact_path):
        os.makedirs(artifact_path)
    file_path = os.path.join(artifact_path, "output.txt")

    with open(file_path, "w") as f:
        f.write("This is a test artifact.")

    # Log the artifact
    mlflow.log_artifacts(artifact_path)

    # Optional: Print the run ID
    print("Run ID:", mlflow.active_run().info.run_id)

# Explicitly close the active MLflow run, if you are not using the above with keyword
# mlflow.end_run()
```


---

**Previous**: [Model Observability](../../model-observability/model-observability.md) | **Next**: [Experiment Tracking Model Training](experiment-tracking-model-training.md)
