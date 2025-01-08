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