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

<!-- #region -->
### Using Practicus AI Studio with Airflow

You can use Practicus AI Studio for the following tasks for Airflow workflows.

#### Practicus AI Studio functionality for Airflow
- **Explore** data sources such as Data Lakes, Data Warehouses and Databases
- **Transform** data
- **Join** data from different data sources
- **Export** the result to any data source
- Perform these tasks on **individual Workers** or on **distributed Spark** cluster
- **Generate data processing steps** as Python code
- **Auto-detect dependencies** between taks
- **Generate the DAG** code 
- **Export data connection files** separately so you can change them later


#### Sample scenario
- Load **some_table** from a Database A
    - Make changes
    - Save to Dabatase B
- Load **some_other_table** from a Data Lake C
    - Make changes
    - Save to Data Warehouse D
- Load **final_table** from Database E
    - **Join** to some_table
    - **Join** to some_other_table
    - Make other changes
    - Save to Data Lake F
    - **Export everything to Airflow**

Let's take a quick look on the experience.
<!-- #endregion -->

```python
import json
import base64

# Path to your notebook
notebook_path = "intro.ipynb"

# Load the notebook JSON
with open(notebook_path, "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Find the image in the attachments
for cell in notebook["cells"]:
    if "attachments" in cell:
        for attachment, data in cell["attachments"].items():
            for mime, b64_data in data.items():
                # Decode and save the image
                with open(attachment, "wb") as img_file:
                    img_file.write(base64.b64decode(b64_data))
                print(f"Saved: {attachment}")

```

#### Joining data sources

- **Left joining** final_table with column ID to some_other_table column ID

![join.png](img/join.png)


#### Exporting to Airflow

- Practicus AI automatically detects the dependency:
- Operations on **some_table** and **some_other_table** can **execute in parallel** since they do not depend on each other
- If both are successful, operations on **final_table** can happen including **joins**

![airflow](img/airflow.png)


#### Viewing the exported code

- After the code export is completed you can update 4 types of files:
- `.py files:` Each are tasks that include the data processing steps, SQL etc.
- `.._worker.json files:` Defines the worker that each task will run on.
    - Container image to use, worker capacity (CPU, GPU, RAM) ..
- `.._conn.json files:` Defines how to **read data** for each task.
    - Note: Data source credentials can be stored in the Practicus AI data catalog.
- `.._save_conn.json files:` Defines how to **write data** for each task.
    - Note: Data source credentials can be stored in the Practicus AI data catalog.
- `.._join_.._conn.json files:` Defines how each join operation will work: how to **read data** and where to join.
- `.._dag.py file:` The DAG file that brings everything together.

Sample view from the embedded Jupyter notebook inside Practicus AI Studio.

![airflow.png](img/exported.png)


### Airflow deployment options

You have 2 options to deploy to Airflow from Practicus AI Studio.

#### Self-service
- Select the schedule and deploy directly to Airflow add-on service that **an admin gave you access to.**
- This will instantly start the Airflow schedule.
- You can then view your DAGs using Practicus AI and monitor the state of your workflows.
- You can also manually trigger DAGs.

#### Working with a Data Engineer (recommended for sensitive data)
- Just export the code and share with a Data Engineer, so they can:
- Validate your steps (.py files)
- Update data sources for production databases (conn.json files)
- Select appropriate Worker capacity (worker.json files)
- Select appropriate Worker user credentials (worker.json files)
- Deploy to Airflow 
- Define the necesary monitoring steps with automation (e.g. with Practicus AI observability)


---

**Previous**: [Airflow](../airflow/airflow.md) | **Next**: [Build](../../generative-ai/app-building/build.md)
