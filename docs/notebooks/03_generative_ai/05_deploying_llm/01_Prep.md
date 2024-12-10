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

# Sample LLM Deployment with Practicus AI


##### Deploying an LLM (Large Language Model) with Practicus AI involves a series of straightforward steps designed to get your model up and running swiftly. 


### Step 1: Request Model Access


#### First, you need to obtain access to download the model. Visit Meta's LLaMA Downloads page and request access. 
##### https://ai.meta.com/resources/models-and-libraries/llama-downloads/

##### Once approved, you will receive an email with a download URL, active for 24 hours, resembling the following format:


##### https://download.llamameta.net/*?Policy=eyJ...



### Step 2: Clone the LLaMA Repo

<!-- #region jp-MarkdownHeadingCollapsed=true -->
##### cd ~/shared/practicus/codellama
##### git clone https://github.com/facebookresearch/codellama.git

<!-- #endregion -->

### Step 3: Install Dependencies and Download the Model



##### Before downloading the model, ensure wget is installed in your Jupyter terminal:



##### sudo apt-get update
##### sudo apt-get install wget



##### Now, proceed to download the specific model version you're interested in, for instance, the 7b-Instruct model:


##### cd ~/shared/practicus/codellama/codellama
##### bash download.sh



### Step 4: Prepare the Model Directory


##### mkdir ~/shared/practicus/codellama/cache || echo "exists"
##### mv ~/shared/practicus/codellama/codellama/CodeLlama-7b-Instruct ~/shared/practicus/codellama/cache



### Step 5: Install the LLaMA Python Library


##### Navigate to the LLaMA library directory to install it. This might also involve simply copying the LLaMA folder to your code execution directory or automatically downloading it from cached files in the model host:


##### cd ~/shared/practicus/codellama/codellama
##### python3 -m pip install .



### Step 6: Copy LLaMA Python Files to Cache


##### Since the LLaMA library might not be installable via pip, you'll need to manually copy it to a cache directory. This step ensures the library is accessible to the model host:


##### cp -r ~/shared/practicus/codellama/codellama/llama ~/shared/practicus/codellama/cache/codellama-01



### Step 7: Upload Cache to Object Storage



##### Using the upload_download.ipynb notebook, upload the prepared cache directory to your object storage. This action facilitates easy access to the model and its dependencies.


### Step 8: Create New Model Versions with deploy.ipynb


##### Utilize the deploy.ipynb notebook to create new versions of your model. This notebook guides you through the process of deploying your model to the Practicus AI environment.


### Step 9: Use consume.ipynb to Query Your Model



##### Finally, with your model deployed, use the consume.ipynb notebook to send queries to your model. This notebook is your interface for interacting with the LLM, allowing you to test its capabilities and ensure it's functioning as expected.

##### By following these steps, you'll have your LLM deployed and ready for use with Practicus AI. This guide is crafted to ensure a seamless and straightforward deployment process, enabling you to focus on leveraging the model's capabilities for your projects.


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

**Previous**: [Milvus](../04_vector_databases/milvus.md) | **Next**: [Upload Download](02_upload_download.md)
