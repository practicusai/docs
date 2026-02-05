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

```python
import practicuscore as prt

region = prt.get_default_region()
addons_df = prt.addons.get_list().to_pandas()

print("Add-on services accessible to you:")
display(addons_df)

airflow_services_df = addons_df[addons_df["service_type"] == "Airflow"]
print("Airflow services you can access:")
display(airflow_services_df)

if airflow_services_df.empty:
    raise RuntimeError("No Airflow service access. Contact your admin.")

service_key = airflow_services_df.iloc[0]["key"]
service_url = airflow_services_df.iloc[0]["url"]

print("Selected Airflow Service:")
print(f"- Service Key: {service_key}")
print(f"- Service URL: {service_url}")
```

Edit default_worker.json file with your credentials before deploying DAG!

```python
dag_key = "run_task_safe"

prt.workflows.deploy(
    service_key=service_key,
    dag_key=dag_key,
    files_path=None,  # Current directory
)
```


## Supplementary Files

### default_worker.json
```json
{"worker_image":"practicus","worker_size":"Small","service_url":"","email":"","refresh_token":""}
```

### run_task_safe_dag.py
```python
# Airflow DAG run_task_safe_dag.py created using Practicus AI

import logging
from datetime import datetime
from airflow.decorators import dag, task
import practicuscore as prt
import os

# Constructing a Unique DAG ID
# ----------------------------
# We strongly recommend using a DAG ID format like:
#    <dag_key>.<username>
# This approach ensures the username effectively serves as a namespace,
#    preventing name collisions in Airflow.

# Let's locate dag_key and username. This runs in Airflow 'after' deployment.
dag_key, username = prt.workflows.get_dag_info(__file__)
dag_id = f"{dag_key}.{username}"


def convert_local(d):
    logging.debug("Converting {}".format(d))
    return d.in_timezone("Europe/Istanbul")


def _read_cloud_worker_config_from_file(worker_config_json_path: str) -> dict:
    cloud_worker_conf_dict = {}  # type: ignore[var-annotated]
    try:
        if os.path.exists(worker_config_json_path):
            prt.logger.info(f"Reading Worker config from {worker_config_json_path}")
            with open(worker_config_json_path, "rt") as f:
                content = f.read()
                import json

                cloud_worker_conf_dict = json.loads(content)
        else:
            prt.logger.info(
                f"Worker configuration file {worker_config_json_path} not found. "
                f"Airflow DAG must provide settings via params passed from run DAG UI or global Airflow configuration."
            )
    except:
        prt.logger.error(f"Could not parse Worker config from file {worker_config_json_path}", exc_info=True)
    return cloud_worker_conf_dict


def _get_worker_config_dict(**kwargs) -> dict:
    dag = kwargs["dag"]
    dag_folder = dag.folder

    final_dict = {}

    worker_config_json_path = os.path.join(dag_folder, "default_worker.json")
    prt.logger.debug(f"worker_config_json_path : {worker_config_json_path}")
    if os.path.exists(worker_config_json_path):
        worker_dict_from_json_file = _read_cloud_worker_config_from_file(worker_config_json_path)
        try:
            for key, value in worker_dict_from_json_file.items():
                if value not in [None, "", "None"]:
                    prt.logger.info(
                        f"Updating Worker configuration key '{key}' using "
                        f"task specific worker configuration file: default_worker.json"
                    )
                    final_dict[key] = value
        except:
            prt.logger.error(f"Could not parse param dictionary from {worker_config_json_path}", exc_info=True)

    return final_dict


def _cleanup(**kwargs):
    from datetime import datetime, timezone

    timeout_seconds = 59  # Threshold for considering a Worker as stuck
    _worker_config_dict = _get_worker_config_dict(**kwargs)
    region = prt.regions.region_factory(_worker_config_dict)
    prt.logger.info(f"Found region : {str(region)}")
    # Iterate through all Workers in the region
    for worker in region.worker_list:
        time_since_creation = int((datetime.now(timezone.utc) - worker.creation_time).total_seconds())
        prt.logger.info(
            f"{worker.name} started {time_since_creation} seconds ago and is currently in '{worker.status}' state."
        )
        if worker.status == "Provisioning" and time_since_creation > timeout_seconds:
            prt.logger.warning(
                f"-> Terminating {worker.name} — stuck in 'Provisioning' for more than {timeout_seconds} seconds."
            )
            worker.terminate()


# Define other DAG properties like schedule, retries etc.
@dag(
    dag_id=dag_id,
    schedule_interval=None,
    start_date=datetime(2025, 5, 9, 7, 0),
    default_args={
        "owner": username,
        "retries": 0,
    },
    catchup=False,
    user_defined_macros={"local_tz": convert_local},
    max_active_runs=1,
    params=prt.workflows.get_airflow_params(),
)
def generate_dag():
    # The `task_id` must match the task file (e.g., `my_1st_task.py or my_1st_task.sh`)
    # located in the same folder as this DAG file.
    def run_with_dynamic_param(**kwargs):
        from practicuscore.exceptions import TaskError

        try:
            return prt.workflows.run_airflow_task(**kwargs)
        except TaskError as ex:
            _cleanup(**kwargs)
            raise ex

    task1 = task(run_with_dynamic_param, task_id="task1")()

    # Define how your task will flow
    task1


generate_dag()

```

### task1.py
```python
import practicuscore as prt


def main():
    prt.logger.info("Running task 1 is completed")


if __name__ == "__main__":
    main()

```


---

**Previous**: [API Triggers For Airflow](../api-triggers-for-airflow.md) | **Next**: [Task Parameters](../task-parameters.md)
