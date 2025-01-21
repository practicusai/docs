---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

# Consume LLM API

##### This tutorial demonstrates how to interact with a PracticusAI LLM deployment for making predictions using simple api requests.

##### The workflow illustrates obtaining a session token, invoking the LLM API endpoint, and processing responses in parallel.


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
api_url = None # e.g. 'https://company.practicus.com/llm-models/llama-1b-basic-test/'
```

```python
assert api_url, "Please enter your model api url."
```

##### Use the PracticusAI SDK to generate a session token, ensuring secure access to the LLM API.

```python
import practicuscore as prt


token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

##### Send a GET request with the session token to check if the model and its API are active and ready for use.

```python
from requests import get

headers = {'authorization': f'Bearer {token}'}
r = get(api_url + '?get_meta=true', headers=headers)

print('Model details: ', r.text)
if r.status_code != 200:
    print(f"Error code {r.status_code}")
```

##### Interacting with the LLM API to retrieve a response, measuring performance, and analyzing the results

```python
from requests import get
import json

# Provide a user prompt to the LLM API and retrieve the generated response.
data = {
    #'system_context': '',
    'user_prompt': "Who is Einstein?"
    }
r = get(api_url, headers=headers, json=data)

if r.status_code != 200:
    print(f"Error code {r.status_code}")

# Print API response for generated prediction
print('Prediction result:')
try:
    parsed = json.loads(r.text)
    print(json.dumps(parsed, indent=1))
except:
    print(r.text)

# Examine response headers for debugging or additional metadata about the request.
print("Headers: ", r.headers)
```


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

**Previous**: [Deploy](deploy.md) | **Next**: [LangChain Deployment > Model](../langchain-deployment/model.md)
