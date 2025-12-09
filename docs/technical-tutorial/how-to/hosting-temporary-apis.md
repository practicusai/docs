---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Hosting Temporary APIs on Practicus AI Workers

This example demonstrates how Practicus AI Workers can quickly set up temporary APIs for testing purposes without the need to deploy full Practicus AI Apps or Model hosting. This method enables rapid prototyping, proof of concepts, and quick iterations to verify specific functionalities.

**Important:** This is intended for temporary use and prototyping within the Practicus AI Apps environment, not for long-term deployments.

Start by creating a FastAPI app (`main.py`) as shown below.

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Selecting a Port for Your Test Server

Choose an available port from the following options, ensuring it doesn't conflict with existing local services:

- `5500` (Default MLFlow port)
- `8501` (Default Streamlit port)
- `4040` (Default Spark UI port)
- `51000` (Plot service port)

**Example:**  
If you choose port `5500`, make sure your local MLFlow server isn't running.

### Starting the FastAPI Server

Run the following command in your terminal, ensuring you're in the same directory as your `main.py` file:

```shell
uvicorn --host=0.0.0.0 --port=5500 main:app --reload



### Generating the Internal URL for Kubernetes

Each Practicus AI Worker instance has a unique instance ID. Use the following cell to obtain this ID and create a Kubernetes-internal URL.  
- **Note:** This internal URL is accessible only from other Practicus AI Workers or Apps within the same Kubernetes environment.
- **Tip:** You can find the worker's instance ID in your browser's URL bar when viewing the Practicus AI Worker environment.


```python
import practicuscore as prt

instance_id = prt.get_local_worker().instance_id
assert instance_id, "Worker instance Id could not be detected"
print("Worker instance id:")
print(instance_id)

port = 5500
internal_url = f"http://prt-svc-wn-{instance_id}:{port}"
print("Test server url to use inside Kubernetes:")
print(internal_url)
```

### Testing Your Server

Execute the following cells to verify your FastAPI server's functionality from within the Kubernetes environment.

The expected response is:

```json
{"message":"Hello World"}


```python
import requests

resp = requests.get(internal_url)

print(resp.text)
# Prints: {"message":"Hello World"}
```

### (Optional) Generating a Fully Qualified Domain Name (FQDN) URL

If you're working across multiple Kubernetes namespaces, it's advisable to use fully qualified domain names (FQDNs).  
Use the cell below to generate an FQDN URL for internal access to your FastAPI server.


```python
# Deploying on multiple Kubernetes Namespaces? Use Fully qualified domain names (fqdn)
import os

k8s_namespace = os.getenv("PRT_NAMESPACE")
assert k8s_namespace, "Kubernetes namespace could not be detected"
print("Current Kubernetes namespace:")
print(k8s_namespace)
fqdn_internal_url = f"http://prt-svc-wn-{instance_id}.{k8s_namespace}.svc.cluster.local:{port}"
print("Test server fqdn url to use inside Kubernetes:")
print(fqdn_internal_url)
```

```python
import requests

resp = requests.get(fqdn_internal_url)

print(resp.text)
# Prints: {"message":"Hello World"}
```


---

**Previous**: [Customize Templates](customize-templates.md) | **Next**: [Integrate Git](integrate-git.md)
