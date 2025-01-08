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

# Consume LLM API With ChatPracticus

##### This tutorial demonstrates how to interact with a PracticusAI LLM deployment for making predictions using the PracticusAI SDK. The methods used include `ChatPracticus` for invoking the model endpoint and `practicuscore` for managing API tokens.

##### The workflow illustrates obtaining a session token, invoking the LLM API endpoint, and processing responses in parallel.

```python
from langchain_practicus import ChatPracticus
import practicuscore as prt
```

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
api_url = None # Model API e.g. "https://company.practicus.com/llm-models/llama-3b-chain-test/"
```

```python
assert api_url, "Please enter your model api url."
```

##### The `test_langchain_practicus` function is defined to interact with the PracticusAI model endpoint. It uses the `ChatPracticus` object to invoke the API with the provided URL, token, and input data. The response is printed in two formats: a raw dictionary and its content.

```python
def test_langchain_practicus(api_url, token, inputs):
    chat = ChatPracticus(
        endpoint_url=api_url,
        api_token=token,
        model_id="current models ignore this",
    )
    
    response = chat.invoke(input=inputs)

    print("\n\nReceived response:\n", dict(response))
    print("\n\nReceived Content:\n", response.content)
```

##### We retrieve an API session token using PracticusAI SDK. This token is required to authenticate and interact with the PracticusAI deployment.

##### The method below creates a token that is valid for 4 hours, longer tokens can be retrieved from the admin console.

```python

token = prt.models.get_session_token(api_url)
print("API session token:", token)
```

##### We invoke the `test_langchain_practicus` function with the API URL, session token, and an example query, `'What is the capital of England?'`. The function sends the query to the PracticusAI endpoint and prints the received response.

```python
test_langchain_practicus(api_url, token, ['What is the capital of England?'])
```

# Consume LLM API With basic HTTP requests


##### Use the PracticusAI SDK to generate a session token, ensuring secure access to the LLM API.

```python
import practicuscore as prt

# We will be using using the SDK to get a session token.
api_url = None # Model API e.g. "https://company.practicus.com/llm-models/llama-3b-chain-test/"
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
    'user_prompt': "Who is Nikola Tesla?"
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
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse
import json

generator = None
answers = ""


async def init(model_meta=None, *args, **kwargs):
    global generator
    if generator is not None:
        print("generator exists, using")
        return

    print("generator is none, building")
    model_cache = "/var/practicus/cache"
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

    # For basic text-in, text-out task:
    if "user_prompt" in payload_dict:
            
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
    
    # For langchain applications:
    else: 
        
        from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse

        # The payload dictionary is validated against PrtLangRequest.
        practicus_llm_req = PrtLangRequest.model_validate(payload_dict)
        
        # Converts the validated request object to a dictionary.
        data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)
        payload = json.loads(data_js)
        
        # Joins the content field from all messages in the payload to form the prompt string.
        prompt = " ".join([item['content'] for item in payload['messages']])

        # Generate a response from the model
        response = generator(prompt)
        answer = response[0]['generated_text']

        # Creates a PrtLangResponse object with the generated content and metadata about the language model and token usage
        resp = PrtLangResponse(
            content=answer,
            lang_model=payload['lang_model'],
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            # additional_kwargs={
            #     "some_additional_info": "test 123",
            # },
        )

        return resp
```


---

**Previous**: [Deploy](deploy.md) | **Next**: [Cv Asistant > Cv Asistant](../../cv-asistant/cv-asistant.md)
