from practicuscore.gen_ai import PrtLangRequest, PrtLangResponse
import json

model = None


async def init(model_meta=None, *args, **kwargs):
    print("Initializing model")
    global model
    # Initialize your LLM model as usual


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")
    # Add your clean-up code here


async def predict(payload_dict: dict, **kwargs):
    try:
        req = PrtLangRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid PrtLangRequest request. {ex}") from ex

    # Converts the validated request object to a dictionary.
    data_js = req.model_dump_json(indent=2, exclude_unset=True)
    payload = json.loads(data_js)

    # Joins the content field from all messages in the payload to form the prompt string.
    prompt = " ".join([item["content"] for item in payload["messages"]])

    answer = f"You asked:\n{prompt}\nAnd I don't know how to respond yet."

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
