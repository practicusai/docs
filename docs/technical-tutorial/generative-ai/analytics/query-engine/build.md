---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: practicus
    language: python
    name: practicus
---

# Agentic Analytics: Query Engine

This document demonstrates how to build and deploy a query engine that an LLM-powered assistant (like the **Practicus AI Assistant**) can use to answer natural language questions about your data. This is the essence of the _"Talk to Your Data"_ experience.

## The User Experience

The magic happens when a user asks a question like:

> "*What were our most profitable product categories in the last quarter?*"

With the right system prompt and a set of powerful tools, the Practicus AI Assistant orchestrates a series of actions:

1.  **Metadata Search**: The assistant first uses a tool (not shown here, but part of the platform) to search the metadata system (we will use Practicus AI Open Metadata Add-on in this document) for relevant tables. It might find `fact_sales` and `dim_products`.
2.  **SQL Generation**: The LLM generates a SQL query (we will use Trino in this document) to join these tables, filter by date, and aggregate by profit.
3.  **SQL Execution**: It calls our `/run-sql` tool (API endpoint) to execute the query. This execution is governed by the **Policy Engine** we defined separately, ensuring the agent (acting on behalf of the user) can't access unauthorized data, sensitive columns are masked, rows are filtered etc.
4.  **Answer & Follow-up**: The agent gets the data back (as a CSV string), synthesizes a natural language answer, and presents it to the user. It then proactively asks, "*Would you like me to create a chart for this?*"
5.  **Visualization**: If the user agrees, the agent calls our `/create-analytics-dataset` tool, which creates a new virtual dataset in an analytic system such as Practicus AI Apache Superset Add-on and returns a URL. The assistant then opens this URL for the user to explore visually.

This documentation covers the implementation of steps 3 and 5. For steps 1 and 2 please view the previous pages.


### Core SDK Components

Our APIs will be wrappers around powerful helpers from the Practicus AI SDK:

- `prt.sql.execute_sql_async()`: A high-level, safe wrapper for running Trino queries. It automatically handles connection, impersonation, and most importantly, **enforces query limits** to prevent accidental resource-heavy queries.
- `prt.sql.create_analytics_dataset_async()`: An abstraction over the Apache Superset API that simplifies the creation of virtual datasets from a SQL query.
- `prt.sql.parse()`: (Optional) A robust SQL parser. It can extract tables, columns, and limits from a SQL string. This can be crucial for pre-flight validation, especially in environments where Trino's policy engine isn't available and the API must enforce policies itself. 


### API Implementation

We will create, `api/trino_runner.py` and `api/superset_manager.py`, to house all our LLM-callable tools. The clear Pydantic models and docstrings are essential, as they are automatically converted into a schema that the LLM uses to understand how to call the function.


### Tool Breakdown

#### Trino Runner (`/run-sql`)

This is the workhorse. It takes a SQL string and executes it. The use of `prt.sql.execute_sql_async` is key:

* **Security**: It passes the `requester`'s username for impersonation in Trino. This means all policies from our Trino Policy Engine are automatically applied.
* **Safety**: It enforces a `limit` of 100 rows, preventing the LLM from accidentally running a query that returns millions of rows and overwhelming the system or incurring large costs.

#### Superset Dataset Creator (`/create-analytics-dataset`)

This tool bridges the gap between raw data and visualization. By taking the same SQL that produced the answer, it creates a persistent, shareable link in Superset. The `prt.sql.create_analytics_dataset_async` helper abstracts away the complexities of Superset's multi-step API process (authentication, dataset creation, etc.).

### Access Control & Caching Considerations

* **Superset Trino Impersonation**: This feature should be enabled to ensure that Superset queries are executed on behalf of the user. This allows our Trino engine to apply row-level, column-level, and other policies based on the actual user identity.

* **Caching Impact**: When impersonation is enabled, Superset disables query result caching, since cached results would bypass per-user access controls.

* **Recommendation**: For high-performance shared dashboards, consider maintaining a second Trino connection **without impersonation**. Use this for curated, "golden" dashboards, and control access at the Superset level via its own RBAC system.


### Deploying the Agent Tools API

Similar to the policy engine, we deploy this suite of tools as a single Practicus AI App. The platform exposes them as secure endpoints that the LLM client such as Practicus AI Assistant can be configured to use.

```python
app_deployment_key = None
app_prefix = "apps"
```

```python
assert app_deployment_key, "Please select an app deployment setting."
assert app_prefix, "Please select an app prefix."
```

```python
# (Recommended) Analyze the App before deployment
import practicuscore as prt

prt.apps.analyze()
```

```python
app_name = "query"
visible_name = "Query Engine"
description = "Query and analytics engine app"
icon = "fa-chart-pie"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("Booting API:", api_url)
print("API Docs   :", api_url + "redoc/")
```


## Supplementary Files

### api/superset_manager.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field


class AnalyticsConn:
    """Stores Superset connection details. Use environment variables or prt.vault in production!"""

    superset_base_url = "https://analytics.practicus.my-company.com"
    # To create new Superset user, you can run the below on a Superset instance:
    # superset fab create-admin --username api_user --firstname API --lastname User --email ..@.. --password ..
    api_username = "superset_api_user"
    # For production use prt.vault or other secure method
    api_password = "secure_superset_api_password"
    db_name = "Trino"  # The name of the database connection in Superset
    database_id: int | None = None  # Cached DB ID


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low,
)


class CreateDatasetRequest(BaseModel):
    sql: str = Field(
        ...,
        description="The SQL query used to create the analytics dataset. "
        "It's best to use the exact same SQL that generated the data for the user's answer.",
    )
    dataset_name: str = Field(..., description="A short, descriptive name for the dataset (max 25 chars).")


class CreateDatasetResponse(BaseModel):
    dataset_url: str = Field(..., description="The URL to explore the newly created dataset in the analytics system.")


@prt.api("/create-analytics-dataset", spec=api_spec)
async def create_analytics_dataset(payload: CreateDatasetRequest, requester: dict, **kwargs) -> CreateDatasetResponse:
    """
    Creates a virtual dataset in Apache Superset from a SQL query.
    Returns a URL for the user to visualize the data.
    """
    username = requester.get("username")
    if not username:
        raise PermissionError("Could not identify the requesting user.")

    # Find the Superset Database ID once and cache it
    if not AnalyticsConn.database_id:
        db_id = await prt.sql.find_analytics_database_id_async(
            base_url=AnalyticsConn.superset_base_url,
            username=AnalyticsConn.api_username,
            password=AnalyticsConn.api_password,
            db_name=AnalyticsConn.db_name,
        )
        if not db_id:
            raise NameError(f"Could not find a database named '{AnalyticsConn.db_name}' in Superset.")
        AnalyticsConn.database_id = db_id

    dataset_url = await prt.sql.create_analytics_dataset_async(
        base_url=AnalyticsConn.superset_base_url,
        username=AnalyticsConn.api_username,
        password=AnalyticsConn.api_password,
        db_id=AnalyticsConn.database_id,
        sql=payload.sql,
        dataset_name=payload.dataset_name,
        requesting_username=username,  # Adds the user's name to the dataset title for clarity
        add_timestamp=True,  # Ensures dataset name is unique
        limit=1000,  # Enforce a reasonable limit for visualization
        auto_add_limit=True,
    )

    if not dataset_url:
        raise ConnectionError("Failed to create the dataset in the analytics system.")

    return CreateDatasetResponse(dataset_url=dataset_url)

```

### api/trino_runner.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field

api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low,
)


class SQLRequest(BaseModel):
    sql: str = Field(
        ...,
        description="The Trino SQL to run. Must use `catalog.schema.table` and not end with a semicolon. "
        "The query will be limited to 100 rows for safety.",
    )


class SQLResponse(BaseModel):
    result: str = Field(..., description="The result of the SQL query, formatted as a CSV string.")


class DBConn:
    """Stores Trino connection details. Use environment variables or prt.vault in production!"""

    host = "practicus-trino-trino.prt-ns-trino.svc.cluster.local"
    port = 8443
    verify = "/path/to/your/ca_cert.pem"  # Path to your CA cert for TLS
    db_user = "api_user"  # A service user for making the connection
    db_password = "secure_password_for_api_user"


@prt.api("/run-sql", spec=api_spec)
async def run_sql(payload: SQLRequest, requester: dict, **kwargs) -> SQLResponse:
    """
    Runs a Trino SQL query and returns the result. Enforces a 100-row limit.
    The query is executed on behalf of the requesting user for policy enforcement.
    """
    username = requester.get("username")
    if not username:
        raise PermissionError("Could not identify the requesting user.")

    result_csv = await prt.sql.execute_sql_async(
        sql=payload.sql,
        host=DBConn.host,
        port=DBConn.port,
        db_user=DBConn.db_user,
        db_password=DBConn.db_password,
        verify=DBConn.verify,
        impersonate_user=username,  # CRITICAL: This tells Trino to apply policies for the end-user
        limit=100,  # SAFETY: Prevents runaway queries
        auto_add_limit=True,
    )
    return SQLResponse(result=result_csv)

```


---

**Previous**: [Build](../policy-engine/build.md) | **Next**: [Distributed Computing > Introduction](../../../distributed-computing/introduction.md)
