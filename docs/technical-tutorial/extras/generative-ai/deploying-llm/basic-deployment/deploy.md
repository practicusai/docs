---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

# Deploy



##### Deploying a model with Practicus AI involves a sequence of steps designed to securely and efficiently transition a model from development to a production-ready state. Here's a step-by-step explanation, aimed at providing clarity and guidance:

```python
import practicuscore as prt
region = prt.get_region() # The region where the deployments are stored
```

### Defining parameters.
 
##### This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
_deployment_key = None # e.g. "llm-depl"
_prefix = None # e.g. "llm-models"
_model_name = None # e.g. "llama-1b-basic-test"
```

```python
assert _deployment_key and _prefix and _model_name, "Please enter your deployment parameters."
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:

```python
# Let's list our model prefixes and select one of them.
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
```

```python
# Let's list our model deployments and select one of them.
my_model_deployments = region.model_deployment_list
display(my_model_deployments.to_pandas())
```

### Deploying the Model


```python
prt.models.deploy(
    deployment_key=_deployment_key,
    prefix=_prefix, 
    model_name=_model_name, 
    model_dir=None # Current dir
)
```

##### Model Deployment: A call to deploy() initiates the deployment process. It requires the host URL, the obtained auth_token, and other previously defined parameters.
##### Feedback: Upon successful deployment, you'll receive a confirmation. If authentication fails or other issues arise, you'll be prompted with an error message to help diagnose and resolve the issue.


### Summary



##### This process encapsulates a secure and structured approach to model deployment in Practicus AI, leveraging the DataPipeline for effective model management. By following these steps, you ensure that your model is deployed to the right environment with the appropriate configurations, ready for inference at scale. This systematic approach not only simplifies the deployment process but also emphasizes security and organization, critical factors for successful AI project implementations.


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

**Previous**: [Model Json](model-json.md) | **Next**: [Consume Parallel](consume-parallel.md)
