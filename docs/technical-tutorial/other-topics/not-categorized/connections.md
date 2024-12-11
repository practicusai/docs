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

## Practicus AI Connections


### Data Upload to S3-Compatible Storage with the Practicus SDK

This notebook demonstrates how to securely and efficiently upload local data 
from a specified folder to an S3-compatible storage solution—such as Amazon S3, 
MinIO, or other similar services—using the Practicus SDK. As a data scientist, 
you can integrate this step into your data pipelines to simplify dataset management.

By providing your AWS credentials or compatible credentials, as well as optional 
parameters for regions, endpoints, and prefixes, you can:

- Automatically upload large datasets to remote object storage
- Maintain versioned data repositories for improved reproducibility
- Effortlessly share data and results with collaborators or production services

Simply fill in the required parameters below and run the notebook to transfer 
files from this worker or your local machine to the target object storage.


```python
import practicuscore as prt

_aws_access_key_id = None   # AWS Access Key ID or compatible service key
_aws_secret_access_key = None  # AWS Secret Access Key or compatible service secret
_bucket = None  # The name of your target bucket, e.g. "my-data-bucket"

# Ensure that essential parameters are provided
assert _aws_access_key_id and _aws_secret_access_key and _bucket

_aws_session_token = None  # (Optional) AWS session token for temporary credentials
_aws_region = None         # (Optional) Your AWS region. If unknown, you may leave it as None.
_endpoint_url = None       # (Optional) Endpoint URL for S3-compatible services (e.g., MinIO API URL)

_prefix = None  # (Optional) Prefix for organizing objects within the bucket. 
                 # Use None or "" for root-level placement, or specify something 
                 # like "folder" or "folder/subfolder" for nested directories.

_folder_path = None  # The local path containing files to upload.
                     # Example: "/home/ubuntu/your/folder/path/"

_source_path_to_cut = None  # (Optional) A prefix within the local folder path 
                            # that you want to remove from the uploaded object keys.
                            # Leave as None to default to the entire folder path.

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
```

```python

```


---

**Previous**: [Addons](addons.md)
