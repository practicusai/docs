from practicuscore.gen_ai import (
    ChatCompletionRequest, ChatCompletionResponseUsage, ChatCompletionResponseChoiceMessage,
    ChatCompletionResponseChoice, ChatCompletionResponse
)

model = None


async def init(*args, **kwargs):
    print("Initializing model")
    global model

    # Initialize your LLM model as usual


async def predict(payload_dict: dict, **kwargs):
    try:
        req = ChatCompletionRequest.model_validate(payload_dict)
    except Exception as ex:
        raise ValueError(f"Invalid OpenAI ChatCompletionRequest request. {ex}") from ex

    msgs = ""
    for msg in req.messages:
        msgs += f"{(msg.role + ': ') if msg.role else ''}{msg.content}\n"

    # Usage (Optional)
    usage = ChatCompletionResponseUsage(
        prompt_tokens=5,
        completion_tokens=10,
        total_tokens=15
    )

    # Use your LLM model to generate a response.
    # This one just echoes back what the user asks.
    choice_message = ChatCompletionResponseChoiceMessage(
        role="assistant",
        content=f"You asked:\n{msgs}\nAnd I don't know how to respond yet."
    )

    # Create a choice object
    choice = ChatCompletionResponseChoice(
        index=0,
        message=choice_message,
        finish_reason="stop"
    )

    # Finally, create the top-level response object
    open_ai_compatible_response = ChatCompletionResponse(
        choices=[choice],
        # Optional, but recommended fields
        id="chatcmpl-abc123",
        model="gpt-3.5-turbo",
        usage=usage,
    )

    return open_ai_compatible_response
