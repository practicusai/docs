---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (for ML)
    language: python
    name: practicus_ml
---

```python
import practicuscore as prt
import os
import mlflow
```

```python
service_name = "My Mlflow Service"
# You need to configure using the service unique key, you can find your key on the "Practicus AI Admin Console" 
service_key =  ""
# Optionally, you can provide experiment name to create a new experiment while configuring
experiment_name = None
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

**Previous**: [SparkML Ice Cream](../../sparkml/sparkml-ice-cream.md) | **Next**: [Experiment Tracking Model Training](experiment-tracking-model-training.md)
