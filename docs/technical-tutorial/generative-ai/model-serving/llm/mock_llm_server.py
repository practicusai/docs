# A simple echo server you can use to test LLM functionality without GPUs
# Echoes what you request.

import argparse
import logging
import time
from fastapi.responses import PlainTextResponse
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("mock_llm_server")

# Create FastAPI app
app = FastAPI(title="Mock LLM Server")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = 100
    stream: Optional[bool] = False


@app.get("/health")
async def health_check():
    # For testing you might want to add a delay to simulate startup time
    # time.sleep(5)
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    # For testing you might want to add a delay to simulate startup time
    # time.sleep(5)
    return PlainTextResponse("""# HELP some_random_metric Some random metric that the mock server returns
# TYPE some_random_metric counter
some_random_metric 1.23""")


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    # Log the request
    logger.info(f"Received chat request for model: {request.model}")

    # Extract the last message content
    last_message = request.messages[-1].content if request.messages else ""

    # Create a mock response
    response = {
        "id": "mock-response-id",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": f"This is a mock response for: {last_message}"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(last_message.split()),
            "completion_tokens": 8,
            "total_tokens": len(last_message.split()) + 8,
        },
    }

    # Wait a bit to simulate processing time
    time.sleep(0.5)

    return response


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Mock LLM Server")
    parser.add_argument("--port", type=int, default=8585, help="Port to run the server on")
    args = parser.parse_args()

    logger.info(f"Starting mock LLM server on port {args.port}")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=args.port)
