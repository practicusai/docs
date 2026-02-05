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

# Upload to Object Storage


##### In this guide, we'll walk through the process of uploading and downloading model-related files to and from an object storage solution using AWS S3 as an example. This functionality is essential for deploying and managing models in the Practicus AI environment, allowing you to efficiently handle model files, configurations, and other necessary assets. We will use the boto3 library for interacting with AWS services, specifically S3 for object storage.


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
_aws_access_key_id = None
_aws_secret_access_key = None
_bucket = None  # The name of your target bucket, e.g. "my-data-bucket"
_prefix = None  # Your prefix within bucket e.g. cache/llama-1b-instruct/

_folder_path = None  # The local path containing files to upload.
# e.g. "/home/ubuntu/shared/LLM-Models/llama-1B-instruct"

_aws_session_token = None  # (Optional) AWS session token for temporary credentials
_aws_region = None  # (Optional) Your AWS region. If unknown, you may leave it as None.
_endpoint_url = None  # (Optional) Endpoint URL for S3-compatible services (e.g., MinIO API URL)

_prefix = None  # (Optional) Prefix for organizing objects within the bucket.
# Use None or "" for root-level placement, or specify something
# like "folder" or "folder/subfolder" for nested directories.

_source_path_to_cut = None  # (Optional) A prefix within the local folder path
# that you want to remove from the uploaded object keys.
# Leave as None to default to the entire folder path.
```

```python
# Ensure that essential parameters are provided
assert _aws_access_key_id and _aws_secret_access_key and _bucket and _prefix

# Ensure the folder path is provided
assert _folder_path
```

### Step 1: Import Required Libraries


```python
import os
import boto3
```

##### The os module is used for operating system-dependent functionality like reading or writing files, whereas boto3 is the Amazon Web Services (AWS) SDK for Python, allowing you to interact with AWS services including S3.


### Step 2: Uploading Files to Object Storage



##### Define a function upload_files that recursively uploads all files from a specified folder to your S3 bucket. This function is particularly useful for batch uploading model files and associated configurations.

```python
def upload_files(folder_path, bucket_name, prefix, s3_client):
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                # Create the full local path of the file
                full_path = os.path.join(subdir, file)

                # Create the relative path (relative to the folder_path)
                relative_path = os.path.relpath(full_path, folder_path)

                # Use the relative path as the prefix for the S3 object key
                s3_key = relative_path.replace("\\", "/")  # Ensure compatibility with S3 (Unix-style paths)
                s3_key = prefix + s3_key

                # Upload the file
                s3_client.upload_file(full_path, bucket_name, s3_key)

                print(f"Successfully uploaded {relative_path} to {s3_key}")
            except Exception as ex:
                print(f"Failed to upload {relative_path} to {s3_key}\n{ex}")
```

### Step 3: Configure S3 Client and Execute Functions



##### Before executing the upload and download functions, configure your S3 client with your AWS credentials. Ensure your AWS Access Key ID and AWS Secret Access Key are securely stored and not hard-coded or exposed in your scripts.

```python
s3_client = boto3.client("s3", aws_access_key_id=_aws_access_key_id, aws_secret_access_key=_aws_secret_access_key)
```

##### Now, call the upload_files function to upload your model directory to S3.

```python
upload_files(_folder_path, _bucket, _prefix, s3_client)
```

### (OPTIONAL) Use Our SDK to Upload Files to an S3 Bucket


##### You can also conveniently upload files to an S3 bucket using our SDK, which provides seamless integration and simplifies the process.

```python
import practicuscore as prt


_upload_conf = prt.connections.UploadS3Conf(
    bucket=_bucket,
    prefix=_prefix,
    folder_path=_folder_path,
    source_path_to_cut=_source_path_to_cut,
    aws_access_key_id=_aws_access_key_id,
    aws_secret_access_key=_aws_secret_access_key,
)

prt.connections.upload_to_s3(_upload_conf)
```


---

**Previous**: [Model Download](Model-Download.md) | **Next**: [Basic Deployment > Model](../basic-deployment/model.md)
