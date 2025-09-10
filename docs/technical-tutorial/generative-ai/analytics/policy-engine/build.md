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

# Agentic Analytics: Policy Engine

Welcome to the documentation for **Practicus AI's Agentic Analytics** capabilities. This notebook focuses on a core component: the **Policy Engine**. We will be using **Trino**, but other query engines can be supported similarly too. The policy engine enables fine-grained, dynamic, and metadata-driven data access control for your Trino data federation layer.

## The Big Picture: Secure, Context-Aware Data Access

In a modern data stack, providing users and AI agents with access to data is crucial, but so is ensuring security and compliance. Our  Policy Engine acts as a **centralized gatekeeper for all queries** executed through Trino. It **intercepts every query request** and makes a real-time decision based on a set of rules you define.

Instead of hardcoding rules, our engine integrates with **Open Metadata**. This allows you to define policies based on rich, dynamic metadata, such as:

- **User Personas & Teams:** Who is the user? Are they a `DataEngineer`, `DataScientist`, or `BusinessAnalyst`?
- **Data Sensitivity:** Does the requested data contain `PII`?
- **Data Certification & Tier:** Is this a `Tier 1` table? Is it certified (medallian) as `Gold`?
- **Custom tags:** Is this table tagged as `HR.Sensitive`?
  
This approach transforms data governance from a static, manual process into a dynamic, automated system that scales with your organization.


### How It Works

When a user or an LLM agent runs a query on Trino, Trino is configured to call three secure API endpoints that we will build and deploy:

1.  **`/validate`**: Decides if the user is **allowed** to perform the action (e.g., `SELECT`) on the requested tables and columns.
2.  **`/mask-columns`**: Applies dynamic **column masking** for sensitive data. For example, a user might see `****-****-****-1234` instead of a full credit card number.
3.  **`/filter-rows`**: Applies dynamic **row-level security** by injecting `WHERE` clauses into the query. For example, a sales manager might only see data for their own region.

These endpoints use the Practicus AI SDK to fetch user and table metadata from Open Metadata in real-time to make these decisions. Let's look at the implementation.


### API Implementation: `api/trino_policy.py`

Please view the Python code that implements our three policy endpoints. 


### Key Concepts in the Code

#### Initialization
The `init_metadata()` function configures the connection to your Open Metadata instance. It uses `prt.metadata.initialize()`, passing the host, an auth token, and a `catalog_service_map`. This map is crucial because it translates Trino's `catalog` names to Open Metadata's `service` names, allowing the SDK to find the correct metadata entities.

#### Validation (`/validate`)
This mandatory endpoint is the first line of defense. 
- It receives a `prt.TrinoPolicyRequest` payload, which contains the user's identity and the resource they are trying to access.
- It fetches metadata for the user (`prt.metadata.get_user_async`) and the table (`prt.metadata.get_table_async`).
- It then applies logic: for instance, it denies access if a user without the `DataEngineer` persona tries to query columns tagged as `PII.Sensitive`.

#### Column Masking (`/mask-columns`)
- This optional endpoint returns a `prt.TrinoColumnMask` object containing a list of `prt.TrinoColumnMaskRule`s.
- For each sensitive column, you can define a SQL `expression` to replace the original value. This supports both static masks (e.g., `'****'`) and dynamic ones (e.g., showing the last 4 digits).
- 
#### Row Filtering (`/filter-rows`)
- This optional endpoint returns a `prt.TrinoRowFilter` object.
- The `expressions` list contains SQL conditions that Trino will automatically add to the `WHERE` clause of the query, effectively filtering the result set based on the user's permissions.


### Deploying the Policy Engine API

Once the `api/trino_policy.py` file is ready, deploying it as a secure, scalable API is straightforward with the Practicus AI platform. The following command packages and deploys the code from the `/api` directory.

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
app_name = "policy"
visible_name = "Policy Engine"
description = "Policy Engine app"
icon = "fa-user-lock"

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

### api/trino_policy_engine.py
```python
import practicuscore as prt

logger = prt.metadata.logger


def init_metadata():
    """Initializes the connection to the Open Metadata service."""
    logger.info("Initializing metadata client...")
    
    # This map translates Trino catalog names to Open Metadata service names.
    # This is necessary for the SDK to locate the correct table metadata.
    # Format: {"trino_catalog_name": "openmetadata_service_name"}
    catalog_service_map = {
        "prt_analytics_db": "analytics_service",
        "prt_operational_db": "operational_service",
    }

    # Use environment variables or prt.vault in production!
    prt.metadata.initialize(
        host="https://openmetadata.practicus.my-company.com",
        token="your-bot-auth-token-here",  # Use a service account token
        catalog_service_map=catalog_service_map,
    )


# For policy endpoints, authentication is handled by Trino's secure connection,
# so we can disable the built-in authentication layer.
api_spec = prt.APISpec(
    disable_authentication=True,
)


@prt.api("/validate", spec=api_spec)
async def validate(payload: prt.TrinoPolicyRequest, **kwargs):
    """
    Validates if a user is authorized to perform a specific action on a resource.
    This is the primary access control gate.
    """
    if not prt.metadata.initialized:
        init_metadata()

    accept = {"result": True}
    deny = {"result": False}

    user_id = payload.user
    operation = payload.operation

    # (Optional) Automatically approve non-data-access operations for usability with tools like DBeaver.
    auto_accept_ops = [
        "AccessCatalog",
        "ExecuteQuery",
        "ImpersonateUser",
        "FilterCatalogs",
        "FilterSchemas",
        "FilterTables",
        "FilterColumns",
    ]
    if operation in auto_accept_ops:
        logger.info(f"Auto-approving operation: '{operation}' for user: '{user_id}'")
        return accept

    # In this example we only care about SELECT statements. Deny all other operations like INSERT, DELETE, etc.
    if operation != "SelectFromColumns":
        logger.warning(f"Rejecting non-SELECT operation: '{operation}' for user: '{user_id}'")
        return deny

    trino_table = payload.get_table_to_select()
    logger.info(f"Validating access for user '{user_id}' on table '{trino_table.full_name}'")

    try:
        # Fetch metadata for the requested table and the user from Open Metadata
        table_meta = await prt.metadata.get_table_async(trino_table.full_name)
        user_meta = await prt.metadata.get_user_async(user_id)

        # Example POLICY 1: Data Engineers can access anything.
        if "DataEngineer" in user_meta.personas:
            logger.info(f"User '{user_id}' has 'DataEngineer' persona. Approving access.")
            return accept

        # Example POLICY 2: Deny access to any PII columns if the user is not a Data Engineer.
        if table_meta.has_pii():
            requested_pii_columns = table_meta.find_pii_columns(trino_table.columns)
            if requested_pii_columns:
                logger.warning(
                    f"User '{user_id}' requested PII columns {requested_pii_columns} "
                    f"from table '{table_meta.fully_qualified_name}'. Rejecting."
                )
                return deny

        # Example POLICY 3: If we reach here, the access is approved.
        logger.info(f"Access approved for user '{user_id}' to table '{trino_table.full_name}'")
        return accept

    except Exception as e:
        logger.error(f"Policy evaluation failed for table '{trino_table}'. Reason: {e}. Denying access.")
        return deny


@prt.api("/mask-columns", spec=api_spec)
async def mask_columns(payload: prt.TrinoPolicyRequest, **kwargs):
    """Applies column masking rules for sensitive data."""
    if not prt.metadata.initialized:
        init_metadata()

    columns_to_mask = payload.get_columns_to_mask()
    masking_rules: list[prt.TrinoColumnMaskRule] = []

    for column in columns_to_mask:
        # Example Policy: Mask the 'customer_ssn' column in the 'customers' table.
        if column.table_full_name == "prt_operational_db.public.customers" and column.columnName == "customer_ssn":
            logger.info(f"Applying SSN mask for column {column}.")
            # The expression must be valid Trino SQL.
            # Note: It's usually required to CAST the masked value to the column's original type/length (e.g. VARCHAR(10))
            # to avoid type inference issues in Trino.
            expression = f"CAST('***-**-' || SUBSTR({column.columnName}, LENGTH({column.columnName}) - 3, 4) AS VARCHAR(15))"
            rule = prt.TrinoColumnMaskRule(column=column, expression=expression)
            masking_rules.append(rule)

    # Similar to the /validate endpoint, you can implement dynamic policies by pulling metadata of the table
    # first and then checking table/column level tags. E.g. if column has 'HR.Sensitive' tag and the user 
    # is not a 'DataScientist', apply a column mask to return '****' if column is string, Null if it is number ....

    # Note: Please consider adding default policies for system catalog
    
    if masking_rules:
        return prt.TrinoColumnMask(result=masking_rules)

    # Default: No masks
    return prt.TrinoColumnMask(result=[])


@prt.api("/filter-rows", spec=api_spec)
async def filter_rows(payload: prt.TrinoPolicyRequest, **kwargs):
    """Applies row-level security filters based on user attributes."""
    if not prt.metadata.initialized:
        init_metadata()

    trino_table = payload.get_table_to_filter()
    user_id = payload.user

    # Example Policy: In the 'sales_transactions' table, users can only see their own sales.
    # We assume a 'sales_rep_email' column exists in the table.
    if trino_table.full_name == "prt_analytics_db.public.sales_transactions":
        try:
            user_meta = await prt.metadata.get_user_async(user_id)
            user_email = user_meta.email
            logger.info(f"Applying row filter for user '{user_id}' on table '{trino_table.full_name}'")
            # The expression is a standard SQL WHERE clause condition.
            # NOTE: Ensure the column name 'sales_rep_email' and the value are correctly formatted for SQL.
            return prt.TrinoRowFilter(expressions=[f"sales_rep_email = '{user_email}'"])
        except Exception as e:
            logger.error(f"Could not generate row filter for user '{user_id}'. Reason: {e}")
            # Return an impossible condition to prevent data leakage on error
            return prt.TrinoRowFilter(expressions=["1 = 0"])

    # Similar to the /validate endpoint, you can implement dynamic policies by pulling metadata of the table
    # first and then checking table level tags.

    # Note: Please consider adding default policies for system catalog
        
    # Default: No filter
    return prt.TrinoRowFilter(expressions=[])

```


---

**Previous**: [Intro](../intro.md) | **Next**: [Query Engine > Build](../query-engine/build.md)
