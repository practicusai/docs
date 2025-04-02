from practicuscore.gen_ai import (
    PrtEmbeddingsRequest, PrtEmbeddingObject, PrtEmbeddingUsage, PrtEmbeddingsResponse
)

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    # Initialize your embedding model as usual


async def predict(payload_dict: dict, **kwargs):
    try:
        req = PrtEmbeddingsRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid PrtEmbeddingsRequest request. {ex}") from ex
    
    usage = PrtEmbeddingUsage(
        prompt_tokens=5,
        total_tokens=15
    )

    # Generating some random embeddings, replace with the actual model
    embedding = PrtEmbeddingObject(
        embedding=[0.123, 0.345, 0.567, 0.789],
        index=1234
    )
    
    response_obj = PrtEmbeddingsResponse(
        data=[embedding],
        model="an-optional-model-id",
        usage=usage,
    )

    return response_obj
