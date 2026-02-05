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

# Preparation of Model File


##### This section provides a detailed explanation of the code used to deploy a model, catering to both the LangChain-compatible Large Language Model (LLM) API endpoint via the PracticusAI SDK and standard LLM deployments for text-in, text-out tasks. The model.py script serves as the core of this implementation, managing model initialization, payload processing, and response generation. Below, we offer a comprehensive breakdown of each segment:


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


##### sys: Used for interacting with the interpreter, including adding paths for Python to search for modules.
##### datetime: Facilitates recording timestamps, useful for performance monitoring.



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
    model_cache = "/var/practicus/cache"  # for details check 02_model_json
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
        model.to("cpu")  # Change with cuda or auto to use gpus.
        return pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

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
        return {"answer": f"Time:{total_time}\answer:{text}"}

    # For langchaing applications:
    else:
        from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse

        # The payload dictionary is validated against PrtLangRequest.
        practicus_llm_req = PrtLangRequest.model_validate(payload_dict)

        # Converts the validated request object to a dictionary.
        data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)
        payload = json.loads(data_js)

        # Joins the content field from all messages in the payload to form the prompt string.
        prompt = " ".join([item["content"] for item in payload["messages"]])

        # Generate a response from the model
        response = generator(prompt)
        answer = response[0]["generated_text"]

        # Creates a PrtLangResponse object with the generated content and metadata about the language model and token usage
        resp = PrtLangResponse(
            content=answer,
            lang_model=payload["lang_model"],
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            # additional_kwargs={
            #     "some_additional_info": "test 123",
            # },
        )

        return resp
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
        model.to("cpu")  # Change with cuda or auto to use gpus.
        return pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

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
        return {"answer": f"Time:{total_time}\nanswer:{text}"}

    # For langchain applications:
    else:
        from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse

        # The payload dictionary is validated against PrtLangRequest.
        practicus_llm_req = PrtLangRequest.model_validate(payload_dict)

        # Converts the validated request object to a dictionary.
        data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)
        payload = json.loads(data_js)

        # Joins the content field from all messages in the payload to form the prompt string.
        prompt = " ".join([item["content"] for item in payload["messages"]])

        # Generate a response from the model
        response = generator(prompt)
        answer = response[0]["generated_text"]

        # Creates a PrtLangResponse object with the generated content and metadata about the language model and token usage
        resp = PrtLangResponse(
            content=answer,
            lang_model=payload["lang_model"],
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

**Previous**: [Consume Parallel](../langchain-deployment/consume-parallel.md) | **Next**: [Model Json](model-json.md)
