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

# Model.json


##### The provided model.json snippet exemplifies how configuration files are used to specify operational parameters for deploying and running Large Language Models (LLMs) within an ecosystem like Practicus AI. This JSON configuration plays a critical role in streamlining the deployment process, enhancing model management, and ensuring the model operates efficiently within its environment. Here's an explanation of why this model.json content is significant:


### Specifying Resource Locations



##### "download_files_from": "cache/llama-1b-instruct/": 

#### This key-value pair indicates the directory or path from which the necessary model files should be downloaded. In the context of deploying an LLM, these files could include the model weights, tokenizer files, and any other dependencies required for the model to run. This parameter ensures that the deployment system knows where to fetch the model's components, which is crucial for initializing the model in the target environment.


### Customizable Download Target



##### "_comment": "you can also define download_files_to otherwise, /var/practicus/cache is used": This comment within the JSON highlights an optional parameter that could be specified in a similar JSON configuration file. If the download_files_to parameter is provided, it would dictate the destination directory on the local system where the downloaded files should be stored. In the absence of this parameter, a default location (/var/practicus/cache) is used. This flexibility allows for adaptability to different deployment environments and configurations, ensuring that the files are stored in a location that is accessible and appropriate for the model's operation.


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

**Previous**: [Model](model.md) | **Next**: [Deploy](deploy.md)
