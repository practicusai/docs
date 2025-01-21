---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Preparation of Model File


##### The model.py file is a critical component when deploying a Large Language Model (LLM) in environments like Practicus AI. It encapsulates the logic for initializing the model, making predictions, and cleaning up resources. Below, we will provide a detailed explanation of a model.py script designed for deploying an LLM, ensuring no step is overlooked.


### Import Statements


```python
import sys 
from datetime import datetime
```

### Global Variables
 

```python
generator = None
```

##### generator: Holds the model instance. Initialized as None and later assigned the LLM object.


### Initialization Function



##### The `init` function  attempts to import the LLaMA library and build the model with specified parameters.

```python
async def init(model_meta=None, *args, **kwargs):
    global generator
    # Checks if the `generator` is already initialized to avoid redundant model loading.
    if generator is not None:
        print("generator exists, using")
        return
    
    # If `generator` is not already initialised, builds the generator by loading the desired LLM
    print("generator is none, building")
    model_cache = "/var/practicus/cache" # for details check 02_model_json
    if model_cache not in sys.path:
        sys.path.insert(0, model_cache)
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    except Exception as e:
        raise print(f"Failed to import required libraries: {e}")
    
    # Initialize the local LLM model using transformers:
    def load_local_llm(model_path):
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        model.to('cpu') # Change with cuda or auto to use gpus.
        return pipeline('text-generation', model=model, tokenizer=tokenizer, max_new_tokens=200)
    
    try:
        generator = load_local_llm(model_cache)
    except Exception as e:
        print(f"Failed to build generator: {e}")
        raise

```

### Cleanup Function



##### This function is designed to free up resources once they're no longer needed, setting generator back to None and clearing the GPU memory cache to prevent memory leaks, crucial for maintaining performance.

```python
async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")
    global generator
    generator = None
    from torch import cuda
    cuda.empty_cache()
```

### Prediction Wrapper Function



##### The `predict` function processes user input and generates responses using the LLM. Key steps include:

```python
async def predict(payload_dict: dict, **kwargs):

    # Recording the start time to measure execution duration.
    start = datetime.now()

    # Extracting given prompt from the http request
    sentence = payload_dict["user_prompt"]
    
    # Passing the prompt to the `generator`, loaded llm model for generating a response.
    res = generator([sentence])
    text = res[0]

    # Returning a structured response containing the generated text and execution time.
    total_time = (datetime.now() - start).total_seconds()   
    return {
        'answer': f'Time:{total_time}\answer:{text}'
    }
```

### Summary


##### This model.py script outlines a robust framework for deploying and interacting with a LLM in a scalable, asynchronous manner. It highlights essential practices like dynamic library loading, concurrent processing with threads, resource management, and detailed logging for performance monitoring. This setup is adaptable to various models and can be tailored to fit specific requirements of different LLM deployments.


## Supplementary Files

### model.json
```json
{
"download_files_from": "cache/llama-1b-instruct/",
"_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used"
}
```

### model.py
```python
import sys
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse
import json

generator = None

async def init(model_meta=None, *args, **kwargs):
    global generator

    # Checks if the `generator` is already initialized to avoid redundant model loading.
    if generator is not None:
        print("generator exists, using")
        return
    
    # If `generator` is not already initialised, builds the generator by loading the desired LLM
    print("generator is none, building")
    model_cache = "/var/practicus/cache" # for details check 02_model_json
    if model_cache not in sys.path:
        sys.path.insert(0, model_cache)
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    except Exception as e:
        raise print(f"Failed to import required libraries: {e}")
    
    # Initialize the local LLM model using transformers:
    def load_local_llm(model_path):
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        model.to('cpu') # Change with cuda or auto to use gpus.
        return pipeline('text-generation', model=model, tokenizer=tokenizer, max_new_tokens=200)
    
    try:
        generator = load_local_llm(model_cache)
    except Exception as e:
        print(f"Failed to build generator: {e}")
        raise



async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")

    global generator
    generator = None

    from torch import cuda
    cuda.empty_cache()

async def predict(payload_dict: dict, **kwargs):
    
    # Recording the start time to measure execution duration.
    start = datetime.now()

    # Extracting given prompt from the http request
    sentence = payload_dict["user_prompt"]
    
    # Passing the prompt to the `generator`, loaded llm model to generate a response.
    res = generator([sentence])
    text = res[0]

    # Returning a structured response containing the generated text and execution time.
    total_time = (datetime.now() - start).total_seconds()   
    return {
        'answer': f'Time:{total_time}\nanswer:{text}'
    }
```


---

**Previous**: [Upload LLM](../Preparation/Upload-LLM.md) | **Next**: [Model Json](model-json.md)
