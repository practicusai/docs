---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Upload and Download to Object Storage


##### In this guide, we'll walk through the process of uploading and downloading model-related files to and from an object storage solution using AWS S3 as an example. This functionality is essential for deploying and managing models in the Practicus AI environment, allowing you to efficiently handle model files, configurations, and other necessary assets. We will use the boto3 library for interacting with AWS services, specifically S3 for object storage.


### Step 1: Import Required Libraries


```python
import os
import boto3
```

##### The os module is used for operating system-dependent functionality like reading or writing files, whereas boto3 is the Amazon Web Services (AWS) SDK for Python, allowing you to interact with AWS services including S3.


### Step 2: Uploading Files to Object Storage



##### Define a function upload_files that recursively uploads all files from a specified folder to your S3 bucket. This function is particularly useful for batch uploading model files and associated configurations.

```python
def upload_files(folder_path, bucket_name, s3_client):
    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                relative_path = os.path.join(subdir, file)
                s3_client.upload_file(relative_path, bucket_name, relative_path)
                print(f"Successfully uploaded {relative_path}")
            except Exception as ex:
                print(f"Failed to upload {relative_path}\n{ex}")

```

### Step 3: Downloading Files from Object Storage



##### Create a function download_items_with_prefix that downloads files from your S3 bucket that match a specified prefix into a local directory. This is useful for fetching model versions or specific configurations.

```python
def download_items_with_prefix(bucket_name, prefix, local_folder, s3_client):
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get('Contents', []):
            try:
                file_name = obj['Key']
                local_file_path = os.path.join(local_folder, file_name)
                local_file_dir = os.path.dirname(local_file_path)
                if not os.path.exists(local_file_dir):
                    os.makedirs(local_file_dir)
                s3_client.download_file(bucket_name, file_name, local_file_path)
                print(f"Successfully downloaded {file_name} to {local_file_path}")
            except Exception as ex:
                print(f"Failed to download {file_name} to {local_file_path}\n{ex}")

```

### Step 4: Configure S3 Client and Execute Functions



##### Before executing the upload and download functions, configure your S3 client with your AWS credentials. Ensure your AWS Access Key ID and AWS Secret Access Key are securely stored and not hard-coded or exposed in your scripts.

```python
bucket_name = 'your-bucket-name'
aws_access_key_id = 'your-access-key-id'
aws_secret_access_key = 'your-secret-access-key'

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
```

##### Now, call the upload_files function to upload your model directory to S3, and use the download_items_with_prefix function to download specific files or configurations needed for your model deployment.


## Supplementary Files

### model.json
```json
{
"download_files_from": "cache/codellama-01/",
"_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### model.py
```python
import sys
from datetime import datetime

generator = None
answers = ""


async def init(model_meta=None, *args, **kwargs):
    global generator
    if generator is not None:
        print("generator exists, using")
        return

    print("generator is none, building")

    # Assuming llama library is copied into cache dir, in addition to torch .pth files
    llama_cache = "/var/practicus/cache"
    if llama_cache not in sys.path:
        sys.path.insert(0, llama_cache)
        
    try:
        from llama import Llama
    except Exception as e:
        raise ModuleNotFoundError("llama library not found. Have you included it in the object storage cache?") from e
    
    try:
        generator = Llama.build(
            ckpt_dir=f"{llama_cache}/CodeLlama-7b-Instruct/",
            tokenizer_path=f"{llama_cache}/CodeLlama-7b-Instruct/tokenizer.model",
            max_seq_len=512,
            max_batch_size=4,
            model_parallel_size=1
        )
    except:
        building_generator = False
        raise


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")

    global generator
    generator = None

    from torch import cuda
    cuda.empty_cache()


def _predict(http_request=None, model_meta=None, payload_dict=None, *args, **kwargs):
    start = datetime.now()
    
    # instructions = [[
    #     {"role": "system", "content": payload_dict["system_context"]},
    #     {"role": "user", "content": payload_dict["user_prompt"]}
    # ]]

    instructions = [[
        {"role": "system", "content": ""},
        {"role": "user", "content": "Capital of Turkey"}
    ]]

    results = generator.chat_completion(
        instructions,
        max_gen_len=None,
        temperature=0.2,
        top_p=0.95,
    )

    answer = ""
    for result in results:
        answer += f"{result['generation']['content']}\n"

    print("thread answer:", answer)
    total_time = (datetime.now() - start).total_seconds()
    print("thread asnwer in:", total_time)    

    global answers 
    answers += f"start:{start} end: {datetime.now()} time: {total_time} answer: {answer}\n"


async def predict(http_request, model_meta=None, payload_dict=None, *args, **kwargs):
    await init(model_meta)
    
    import threading 
    
    threads = []

    count = int(payload_dict["count"])
    thread_start = datetime.now()
    for _ in range(count):
        thread = threading.Thread(target=_predict)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    print("Total finished in:", (datetime.now() - thread_start).total_seconds())    

    return {
        "answer": f"Time:{(datetime.now() - thread_start).total_seconds()}\nanswers:{answers}"
    }
    

```


---

**Previous**: [Prep](Prep.md) | **Next**: [Model](model.md)
