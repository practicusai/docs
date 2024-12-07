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

### Workflows with Practicus AI Airflow Add-on Service

- Practicus AI provides several add-ons, including Airflow for workflow orchestration.
- This notebook demonstrates how to deploy workflows using Airflow through Practicus AI.

<!-- #region -->
#### (Recommended) Create tasks, Airflow DAG and supporting files

Plan your tasks and divide them into isolated, manageable units:
- **Each task runs fully isolated** on its own Worker (Kubernetes Pod).
- Group related actions into a single task for simplicity.

Generating files:
- Practicus AI can generate files as a **starting point** to develop your workflow.
- An important part of the workflow is the DAG, which is the order and parallelism of the tasks in your flow. For example:
```python
dag_flow = "my_1st_task >> my_2nd_task"
```
- You can define complex task dependencies here, for example:
```python
dag_flow = "my_1st_task >> [my_2nd_task, my_3rd_task] >> my_4th_task"
```
- This flow means:
    - `my_1st_task` runs first.
    - If successful, `my_2nd_task` and `my_3rd_task` run in parallel.
    - Finally, if both succeed, `my_4th_task` runs.
- For more details, see:
    - https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
<!-- #endregion -->

```python
import practicuscore as prt

# Let's define 4 tasks, 2 of which can run in parallel
dag_flow = "my_1st_task >> [my_2nd_task , my_3rd_task] >> my_4th_task"

# Let's define the default worker configuration for *all* tasks
default_worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="X-Small",
)

# Let's define a different worker configuration for the second task:
my_2nd_task_worker_config = prt.WorkerConfig(
    worker_image="practicus-genai",
    worker_size="Small",
)

# You can add as many custom worker configurations as you need in the below 'list of tuples'
custom_worker_configs = [
    ('my_2nd_task', my_2nd_task_worker_config),
]

# Choose a DAG key describing the overall workflow
dag_key = "my_workflow"

# Define a schedule. If None, workflow will only run on-demand
# E.g. @daily
# You can also use cron schedules, E.g.
# For 2 AM, every Thursday you can use '0 2 * * THU'
# For help generating cron schedules: https://crontab.guru
schedule_interval=None

# For dev/test you can fail fast with 0 retires 
# and increase for production
retries=0

prt.workflows.generate_files(
    dag_key=dag_key,
    dag_flow=dag_flow,
    # Optional parameters
    files_path=None,  #  Current dir
    default_worker_config=default_worker_config,
    custom_worker_configs=custom_worker_configs,
    save_credentials=True,
    overwrite_existing=False,
    schedule_interval=schedule_interval,  
    retries=retries,
)
```

#### Understanding the generated files
Now let's take a look at the generated files.
- **`my_1st_task.py to my_4th_task.py`:**
    - These are regular python code that you perform the actions. Please note that each run it's on Worker and fully isolated.
- **`default_worker.json`:**
    - The default container image, size, and login credentials that the workers will run.
    - Pay close attention to credentials, the workflow might not run with your credentials in production.
    - An admin can define the default **system-wide credentials** for all workflows.
    - An end-user can trigger the workflow from Airflow UI and change credentials.
    - Or an admin can alter the worker .json files to add specific credentials before deploying to Airflow.
- **`my_2nd_task_worker.json`:**
    - Similar to above but overrides the worker config for the second task.
    - You can skip adding credentials, in which case the above logic will be applied.
- **`my_workflow_dag.py`:**
    - The Airflow DAG file that brings everything together.

<!-- #region -->
#### (Recommended) Test your tasks before deploying to Airflow

- It is a good idea to test your tasks before deploying to Airflow.
- You can add the below to any task .py file to simulate a failure.
```python
raise SystemError("Simulated error")
```
- To learn more about tasks, please view the tasks sample notebook in parent folder.
<!-- #endregion -->

```python
successful_task_workers, failed_task_workers = prt.workflows.test_tasks(
    dag_flow=dag_flow,
    task_list=None,  # To only test certain tasks
    files_path=None,  #  Current dir
    default_worker_config=default_worker_config,
    custom_worker_configs=custom_worker_configs,
    # Let's terminate workers of successful tasks
    terminate_on_success=True,
    # Let's skip terminating failed task workers to analyze further
    terminate_on_failed=False,
)
```

```python
# Now let's open jupyter notebook to analyze issues

for worker in successful_task_workers:
    # This list will be empty unless you changed terminate_on_success to False.
    print(f"Opening notebook on successful task worker: {worker.name}")
    worker.open_notebook()
    
for worker in failed_task_workers:
    # This list will be empty if all tasks were successful.
    print(f"Opening notebook on failed task worker: {worker.name}")
    worker.open_notebook()

# Do you prefer VS Code over Jupyter? replace worker.open_notebook() with:
# url, token = worker.open_vscode()
```

```python
# Analyze complete? Let's clean-up workers.
   
for worker in successful_task_workers:
    print(f"Terminating successful task worker: {worker.name}")
    worker.terminate()
    
for worker in failed_task_workers:
    print(f"Terminating failed task worker: {worker.name}")   
    worker.terminate()
```

#### (Optional) Search for an Airflow Practicus AI Add-on Service

- Practicus AI add-on's allow you to use different fully isolated services for different purposes, and you can programmatically search for them.
- You can skip this step if you already know the Airflow service key.

```python
import practicuscore as prt

# Retrieve default region and available add-ons
region = prt.get_default_region()
addons_df = region.addon_list.to_pandas()

print("Add-on services that I have access to:")
display(addons_df)

airflow_services_df = addons_df[addons_df["service_type"] == "Airflow"]

print("Airflow services that I have access to:")
display(airflow_services_df)

if airflow_services_df.empty:
    raise RuntimeError(
        "You don't have access to any Airflow service. Please request access from your admin."
    )

# Choosing first available Airflow service, please change accordingly
service_key = airflow_services_df.iloc[0]["key"]
service_url = airflow_services_df.iloc[0]["url"]

print("Selected Airflow Service:")
print(f"Service Key : {service_key}")
print(f"Service URL : {service_url}")
```

```python
# Alternative: manually select an Airflow service key
# service_key = 'my-airflow-service-key'
```

#### Deploy to create or update the workflow on Airflow

- You can now deploy the workflow dag, tasks, and all other supporting files using the below SDK method.
- The code and all artifacts will be stored on the **git source control system** that your selected Airflow service uses.

```python
prt.workflows.deploy(
    service_key=service_key, 
    dag_key=dag_key, 
    files_path=None, # Leave None for current directory
)
```

<!-- #region -->
#### Other Topics

**Running shell scripts**
   - Your task files don't have to be .py files. Shell scripts (.sh) are also supported.

**Manually Creating Worker Configuration Files**
   - Instead of passing `default_worker_config`, `custom_worker_configurations`, and `save_credentials` to `prt.workflows.deploy()`, you can create the worker configuration `.json` files manually.
   - Example configuration file structure:
     ```json
     {
       "worker_image": "practicus",
       "worker_size": "X-Small",
       "service_url": "https://example-service-url",
       "email": "user@example.com",
       "refresh_key": "your-refresh-key"
     }
     ```

**Avoiding Credential Storage**
   - To avoid saving your worker creation credentials (e.g., refresh key) in the default `.json` files, ask your Airflow admin to define these as **global variables** in the Airflow environment.
   - This enhances security by avoiding local storage of sensitive information.

**Manually Passing Credentials**
   - If necessary, you can manually pass credentials while running a DAG using the Airflow UI:
   - Click **Run** on the DAG and provide the required parameters, such as `refresh_key` and `service_url`.

**Deploying to Another Region**
   - By default, `prt.workflows.deploy()` deploys workflows to the current region.
   - To deploy a workflow to a different region:
     ```python
     some_region.deploy_workflow()
     ```
     - First, log in to the target region and then deploy using the region-specific method.

**Geo-Distributed Task Configuration**
   - Each task in your workflow can run in a different region, enabling a **geo-distributed service mesh**.
   - To configure this, create separate worker configuration `.json` files with region-specific details:
     - `service_url`
     - `email`
     - `refresh_key`

   - Example:
     ```json
     {
       "worker_image": "practicus",
       "worker_size": "Small",
       "service_url": "https://us-region.example.com",
       "email": "user-us@example.com",
       "refresh_key": "us-region-refresh-key"
     }
     ```

**Customizing DAG**

- You can customize pretty much everything in the task flow.
- Let's say you are already logging extensively and do not want to capture stdout/stderr output.
- You can customize the dag file to add the below:


```python
def generate_dag():
    # Define a custom task, and make sure task_id matches the task file e.g. my_1st_task.py
    @task(
        task_id="my_1st_task"
    )
    def my_1st_task_updated(**kwargs):
        # Access user-provided or default params
        params = kwargs["params"]

        # Dynamically override parameters at runtime
        if not params.get("capture_task_output"):
            print("User has not set capture_task_output, will default to False")
            params["capture_task_output"] = "False"

        # Run the task as usual
        prt.workflows.run_airflow_task(**kwargs)

    # Comment out the generated task definition
    #   my_1st_task = task(prt.workflows.run_airflow_task, task_id="my_1st_task")()
    # And use your custom task function.
    my_1st_task = my_1st_task_updated()

    # The rest of the DAG code stays the same..
    
    # The `task_id` must match the task file (e.g., `my_1st_task.py`)
    # located in the same folder as this DAG file.
    my_2nd_task = task(prt.workflows.run_airflow_task, task_id="my_2nd_task")()

    # Define how your task will flow
    my_1st_task >> my_2nd_task
```

<!-- #endregion -->
