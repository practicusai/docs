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

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
file_path = None  # e.g. /home/ubuntu/shared/LLM-Models/llama-1B-instruct
REPO_ID = None  # e.g. meta-llama/Llama-3.2-1B-Instruct
hf_token = None  # for details checkout step 1
```

```python
assert file_path, "Please enter a file_path"
assert REPO_ID, "Please enter a REPO_ID"
assert hf_token, "Please enter a hf_token"
```

## Model Download

##### The first step in llm-deployment involves downloading the pre-trained model. These steps include:

##### 1. Authenticating with HuggingFace Hub to securely access model repositories.
##### 2. Getting access to an open source llm model from Hugging Face.
##### 3. Downloading the pre-trained open source LLM (e.g., LLaMA-3B-Instruct, LLaMA-1B-Instruct) from the Hugging Face Hub for deployment.


### Step-1: Authenticating with Hugging Face

##### To download models from the Hugging Face Hub, you must authenticate using your personal API token. This step ensures secure, authorized access to both public and private model repositories.

#### Obtain Your API Token
##### Follow the instructions in the [Hugging Face documentation](https://huggingface.co/docs/hub/security-tokens) to generate or retrieve your API token. Keep this token confidential and do not share it publicly.

#### Authenticate Your Environment
##### After acquiring your token, run the following code to authenticate. This will enable seamless access to the Hugging Face Hub and allow you to download and work with models directly in your environment.

```python
from huggingface_hub.hf_api import HfFolder

HfFolder.save_token(hf_token)  # Replace with your Hugging Face API token
```

### Step-2: Getting access to an open source llm model


#### Second, you need to obtain access to download the model. Visit Meta's LLaMA HuggingFace page and request access. 
##### https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct

##### Once approved, you will receive an e-mail with conformation link, resembling the following format:


##### https://huggingface.co/email_confirmation/bBFX...


### Step 3: Install Dependencies and Download the Model

#### To download a model from Hugging Face Hub we can use the snapshot_download method like down below,

```python
from huggingface_hub import snapshot_download


snapshot_download(repo_id=REPO_ID, local_dir=file_path)
```

##### And to consume the model, we should install the necessary libraries to host service image,

```shell
pip install transformers sentence-transformers langchain langchain-community chromadb pypdf
```

##### If you're unsure how to install the necessary libraries to host the service, we recommend referring to our comprehensive documentation on installing libraries within the Practicus AI environment. It provides clear, step-by-step instructions to ensure a smooth setup process.


##### It is also necessary to install the torch according to the system, you can check the [Torch Installation Document](https://pytorch.org/get-started/locally/).


### Step 4: Upload Cache to Object Storage



##### Using the upload_download.ipynb notebook, upload the downloaded large language model directory to your object storage. This action facilitates easy access to the model and its dependencies.


---

**Previous**: [Introduction](../Introduction.md) | **Next**: [Upload LLM](Upload-LLM.md)
