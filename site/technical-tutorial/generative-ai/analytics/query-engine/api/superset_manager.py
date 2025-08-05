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
