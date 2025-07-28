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
