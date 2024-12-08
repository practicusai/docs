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

# Preparation of Model File


##### The model.py file is a critical component when deploying a Large Language Model (LLM) in environments like Practicus AI. It encapsulates the logic for initializing the model, making predictions, and cleaning up resources. Below, I'll provide a detailed explanation of a model.py script designed for deploying an LLM, ensuring no step is overlooked.


### Import Statements


```python
import sys 
from datetime import datetime
```

##### sys: Used for interacting with the interpreter, including adding paths for Python to search for modules.
##### datetime: Facilitates recording timestamps, useful for performance monitoring.



### Global Variables


```python
generator = None
answers = ""
```

##### generator: Holds the model instance. Initialized as None and later assigned the LLM object.
##### answers: Accumulates responses from the model. Initialized as an empty string and appended with each prediction.


### Initialization Function


```python
async def init(model_meta=None, *args, **kwargs):
    global generator
    if generator is not None:
        print("generator exists, using")
        return

    print("generator is none, building")
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
    except Exception as e:
        print(f"Failed to build generator: {e}")
        raise

```

##### This function prepares the environment for the model. It checks if the generator is already created to avoid redundant loads. If not, it attempts to import the LLaMA library and build the model with specified parameters. Errors in this process trigger exceptions, alerting you to potential issues with library presence or model construction.


### Cleanup Function


```python
async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")
    global generator
    generator = None
    from torch import cuda
    cuda.empty_cache()

```

##### This function is designed to free up resources once they're no longer needed, setting generator back to None and clearing the GPU memory cache to prevent memory leaks, crucial for maintaining performance.


### Prediction Wrapper Function


```python
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

##### This asynchronous function is the main entry for prediction requests. It ensures the model is initialized, then creates and manages multiple threads for concurrent prediction tasks. Each thread calls the _predict function to generate a response. The total execution time is calculated, providing insights into the performance.


### Prediction Execution Function


```python
def _predict(http_request=None, model_meta=None, payload_dict=None, *args, **kwargs):
    start = datetime.now()
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
    print("thread answer in:", total_time)    
    global answers 
    answers += f"start:{start} end: {datetime.now()} time: {total_time} answer: {answer}\n"

```

##### _predict is called by each thread to perform the actual prediction task. It formats the instructions for the model, executes the prediction, and logs the response and execution time. The global answers string is appended with each prediction result for final aggregation.


### Summary



##### This model.py script outlines a robust framework for deploying and interacting with a LLM in a scalable, asynchronous manner. It highlights essential practices like dynamic library loading, concurrent processing with threads, resource management, and detailed logging for performance monitoring. This setup is adaptable to various models and can be tailored to fit specific requirements of different LLM deployments.


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

**Previous**: [Upload Download](02_upload_download.md) | **Next**: [Model Json](04_model_json.md)
