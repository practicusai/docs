---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Workflows with the Practicus AI Airflow Add-on

Practicus AI integrates seamlessly with Airflow to orchestrate workflows. By leveraging Airflow as an add-on, you can:

- Define complex directed acyclic graphs (DAGs) to manage task order and parallelism.
- Schedule tasks to run at specific times or intervals.
- Use Airflow's UI and ecosystem for monitoring and managing workflows.

For more details on Airflow concepts, see the official [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html).

<!-- #region -->
## Creating Tasks, DAGs, and Supporting Files

When building workflows, start by designing your tasks as independently executable units. Each task runs on its own Practicus AI Worker. You can group related actions into a single task for simplicity. Practicus AI provides utilities to generate starter files and DAG definitions.

**Example DAG Flow:**

```python
dag_flow = "my_1st_task >> [my_2nd_task, my_3rd_task] >> my_4th_task"
```

This means:

- `my_1st_task` runs first.
- On success, `my_2nd_task` and `my_3rd_task` run in parallel.
- After both complete, `my_4th_task` runs.

<!-- #endregion -->

```python
import practicuscore as prt

# Define a DAG flow with 4 tasks, where two run in parallel.
dag_flow = "my_1st_task >> [my_2nd_task, my_3rd_task] >> my_4th_task"

# Default worker configuration
default_worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="X-Small",
)

# Custom configuration for the second task
my_2nd_task_worker_config = prt.WorkerConfig(
    worker_image="practicus-genai",
    worker_size="Small",
)

custom_worker_configs = [
    ('my_2nd_task', my_2nd_task_worker_config),
]

dag_key = "my_workflow"
schedule_interval = None  # Set a cron string or '@daily' as needed
retries = 0  # 0 for dev/test, increase for production

prt.workflows.generate_files(
    dag_key=dag_key,
    dag_flow=dag_flow,
    files_path=None,  # Current dir
    default_worker_config=default_worker_config,
    custom_worker_configs=custom_worker_configs,
    save_credentials=True,
    overwrite_existing=False,
    schedule_interval=schedule_interval,
    retries=retries,
)
```

## Understanding the Generated Files

**Task Python Scripts (e.g., `my_1st_task.py`):**

- Contain the logic for each task.
- Each runs in its own isolated Worker.

**`default_worker.json`:**

- Stores default worker configuration (image, size, credentials).
- Credentials can be set globally by an admin or passed at runtime.

**`my_2nd_task_worker.json`:**

- Overrides the worker config for `my_2nd_task`.

**`my_workflow_dag.py`:**

- The Airflow DAG file that ties tasks together.



### Test Your Tasks Before Deploying

It's wise to test tasks locally or via Practicus AI before deploying to Airflow. You can intentionally insert errors in your task code to verify error handling.

For more details on tasks, see the tasks sample notebook. 

```python
successful_task_workers, failed_task_workers = prt.workflows.test_tasks(
    dag_flow=dag_flow,
    task_list=None,  # Test all tasks in the DAG
    files_path=None,  # Current dir
    default_worker_config=default_worker_config,
    custom_worker_configs=custom_worker_configs,
    terminate_on_success=True,   # Automatically terminate successful tasks
    terminate_on_failed=False,  # Keep failed tasks alive for debugging
)
```

```python
# Investigate successful or failed tasks
for worker in successful_task_workers:
    # If you had terminate_on_success=False, you could open the notebook to review logs.
    print(f"Opening notebook on successful task worker: {worker.name}")
    worker.open_notebook()

for worker in failed_task_workers:
    print(f"Opening notebook on failed task worker: {worker.name}")
    worker.open_notebook()
```

```python
# After analysis, terminate remaining workers
for worker in successful_task_workers:
    print(f"Terminating successful task worker: {worker.name}")
    worker.terminate()

for worker in failed_task_workers:
    print(f"Terminating failed task worker: {worker.name}")
    worker.terminate()
```

## (Optional) Locating an Airflow Service Add-on

If you don't know your Airflow service key, you can list available add-ons and identify it. For instructions on add-ons and their usage, see the [Practicus AI documentation](https://docs.practicus.ai).

```python
import practicuscore as prt

region = prt.get_default_region()
addons_df = region.addon_list.to_pandas()

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

```python
# Alternatively, you can set service_key manually if you know it:
# service_key = 'my-airflow-service-key'
```

## Deploying the Workflow to Airflow

Once your tasks, DAG, and configurations are ready and tested, deploy them to Airflow. This pushes your code and configuration to the underlying version control system used by the Airflow service, making the workflow visible and runnable via the Airflow UI.

```python
prt.workflows.deploy(
    service_key=service_key,
    dag_key=dag_key,
    files_path=None,  # Current directory
)
```

## Additional Notes and Customizations

- **Running Shell Scripts:** Tasks don't have to be Python files; `.sh` scripts also work.
- **Manual Worker Config Files:** Instead of passing parameters to `generate_files()` or `deploy()`, you can manually manage the `.json` worker config files.
- **Credential Management:** For security, consider storing credentials globally at the Airflow environment level. Avoid embedding sensitive info in local files.
- **Multi-Region Deployments:** You can create workflows that run tasks in different regions. Just ensure the worker config `.json` files point to the correct `service_url`, `email`, and `refresh_key`.
- **Customizing the DAG:** Edit the generated DAG file to change default parameters, logging settings, or to add custom logic. For complex scenarios (e.g., different logging strategies), you can customize the `run_airflow_task` calls as shown in the example snippet.


---

**Previous**: [Task Basics](../tasks/task-basics.md) | **Next**: [AI Studio > Generating Wokflows](../AI-Studio/generating-wokflows.md)
