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

# Practicus AI Connections



## Displaying Available Connections

Below is a quick way to list all available connections you have. Run the code
to view your configured data sources, storage endpoints, and other services.

```python
import practicuscore as prt

prt.connections.get_all().to_pandas()
```

## Creating a New Connection

The `conn_conf` parameter takes a configuration object from a base class that 
supports many data sources, including:

- S3ConnConf
- SqLiteConnConf
- MYSQLConnConf
- PostgreSQLConnConf
- RedshiftConnConf
- SnowflakeConnConf
- MSSQLConnConf
- OracleConnConf
- HiveConnConf
- ClouderaConnConf
- AthenaConnConf
- ElasticSearchConnConf
- OpenSearchConnConf
- TrinoConnConf
- DremioConnConf
- HanaConnConf
- TeradataConnConf
- Db2ConnConf
- DynamoDBConnConf
- CockroachDBConnConf
- CustomDBConnConf

Here we use `SqLiteConnConf` to create a new SQLite connection by providing
the database file path.

```python
import practicuscore as prt

_name = "New SQLite Connection"
_conn_conf = prt.connections.SqLiteConnConf(file_path="/home/ubuntu/samples/data/chinook.db")

new_conn_uuid = prt.connections.create(name=_name, conn_conf=_conn_conf)
print(new_conn_uuid)

```

## Retrieving a Specific Connection

Retrieve an existing connection by UUID or name to reuse previously configured
settings without reconfiguring them each time.

```python
import practicuscore as prt

_conn_id_or_name = None
assert _conn_id_or_name is not None

conn = prt.connections.get(_conn_id_or_name)
print(conn)
```

## Updating an Existing Connection

After retrieving a connection, you can update its configuration—changing 
file paths, credentials, endpoints, or its name. Provide `_new_conn_conf` 
and `_updated_name` to apply the changes.

```python
import practicuscore as prt

_conn_id_or_name = None
assert _conn_id_or_name is not None
conn = prt.connections.get(_conn_id_or_name)

_new_conn_conf = None  # prt.connections.SqLiteConnConf(file_path="/home/ubuntu/samples/data/chinook.db")
_updated_name = None
assert _new_conn_conf and _updated_name

prt.connections.update(conn_uuid=conn.uuid, name=_updated_name, conn_conf=_new_conn_conf)
```

## Data Upload to S3-Compatible Storage

Upload local data to S3-compatible storage (e.g., Amazon S3, MinIO) using the Practicus SDK.
Provide your credentials, region, endpoints, and prefixes as needed. This approach simplifies
managing datasets remotely, ensures reproducibility, and makes sharing data easier.

Set the parameters below and run the code to transfer files.

```python
import practicuscore as prt

_aws_access_key_id = None   # AWS Access Key ID or compatible service key
_aws_secret_access_key = None  # AWS Secret Access Key or compatible service secret
_bucket = None  # The name of your target bucket, e.g. "my-data-bucket"

# Ensure that essential parameters are provided
assert _aws_access_key_id and _aws_secret_access_key and _bucket

_aws_session_token = None  # (Optional) AWS session token
_aws_region = None         # (Optional) AWS region
_endpoint_url = None       # (Optional) S3-compatible endpoint (e.g., MinIO)

_prefix = None  # (Optional) Prefix for organizing objects within the bucket
_folder_path = None  # The local folder path with files to upload
_source_path_to_cut = None  # (Optional) Remove a leading folder path portion from object keys

# Ensure the folder path is provided
assert _folder_path

_upload_conf = prt.connections.UploadS3Conf(
    bucket=_bucket,
    prefix=_prefix,
    folder_path=_folder_path,
    source_path_to_cut=_source_path_to_cut,
    aws_access_key_id=_aws_access_key_id,
    aws_secret_access_key=_aws_secret_access_key
)

prt.connections.upload_to_s3(_upload_conf)
```


---

**Previous**: [Automated Code Quality](improve-code-quality/automated-code-quality.md) | **Next**: [Integrate Git](integrate-git.md)
