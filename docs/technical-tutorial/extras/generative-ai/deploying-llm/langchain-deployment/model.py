import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse
import json

generator = None

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