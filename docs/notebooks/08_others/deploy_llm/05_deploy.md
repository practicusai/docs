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

# Deploy



##### Deploying a model with Practicus AI involves a sequence of steps designed to securely and efficiently transition a model from development to a production-ready state. Here's a step-by-step explanation, aimed at providing clarity and guidance:


### Step 1: Importing Necessary Modules


```python
import practicuscore as prt
```

### Step 2: Setting Up Deployment Parameters


```python
deployment_key = "deployment-gpu"
prefix = "models/practicus"
model_name = "codellama"
model_dir = None  # Current dir
```

<!-- #region -->
##### Deployment Key: Identifies the deployment configuration, such as compute resources (e.g., GPU or CPU preferences). This key ensures your model is deployed with the appropriate infrastructure for its needs.

##### Prefix: A logical grouping or namespace for your models. This helps in organizing and managing models within Practicus AI.

##### Model Name: A unique identifier for your model within Practicus AI. This name is used to reference and manage the model post-deployment.


##### Model Directory: The directory containing your model's files. If None, it defaults to the current directory from which the deployment script is run.
<!-- #endregion -->

<!-- #region -->
##### Secure Password Entry: getpass.getpass() securely prompts for the password, ensuring it's not visible or stored in plaintext within the script.


##### Authentication Token: dp.get_auth_token() requests an authentication token from Practicus AI, using your email and password. This token is crucial for subsequent API calls to be authenticated.

<!-- #endregion -->

### Step 3: Deploying the Model


```python
prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix, 
    model_name=model_name, 
    model_dir=model_dir
)
```

##### Model Deployment: A call to deploy() initiates the deployment process. It requires the host URL, your email, the obtained auth_token, and other previously defined parameters.
##### Feedback: Upon successful deployment, you'll receive a confirmation. If authentication fails or other issues arise, you'll be prompted with an error message to help diagnose and resolve the issue.


### Summary



##### This process encapsulates a secure and structured approach to model deployment in Practicus AI, leveraging the DataPipeline for effective model management. By following these steps, you ensure that your model is deployed to the right environment with the appropriate configurations, ready for inference at scale. This systematic approach not only simplifies the deployment process but also emphasizes security and organization, critical factors for successful AI project implementations.


## Supplementary Files

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

**Previous**: [Model Json](04_model_json.md) | **Next**: [Consume Parallel](06_consume_parallel.md)
