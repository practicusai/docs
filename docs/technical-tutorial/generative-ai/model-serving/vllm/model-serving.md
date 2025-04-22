---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Practicus AI Large Language Model Hosting

This example demonstrates how to use the Practicus AI SDK `ModelServer` to host LLM models on Practicus AI Model Hosting platform, and also experiment in design time using Practicus AI Workers.



## 1. Overview of ModelServer

`ModelServer` runs and manages LLM inference services, such as `VLLM` (default engine). It provides methods to:

1. Start the server with a given model and options.
2. Secure access and route requests.
3. Monitor and report model health.
4. Monitor and report model metrics.

## High level Usage

```python
import practicuscore as prt
from openai import OpenAI

# Example: start a VLLM server for a Hugging Face model
prt.models.server.start("llama/some-model", {"tensor-parallel-size": 2})

# Get the custom model URL
base_url = prt.models.server.get_base_url()

# Create OpenAI client
client = OpenAI(base_url=base_url, api_key=token)

# Send a chat request
response = client.chat.completions.create(messages=[{"role": "user", "content": "Capital of France?"}], max_tokens=100)

print(response.choices[0].message.content)
```

<!-- #region -->
## Deploying Models

There are multiple options to deploy LLM models for run-time.

### Option 1: Dynamically downloading models in run-time (no-coding required)

Follow the below steps to use an existing container image to dynamically download the model and start serving.

#### Define the container image
- Open Practicus AI management console > Infrastructure > Container Images
- Add a new container image `ghcr.io/practicusai/practicus-modelhost-gpu-vllm:25.5.0` or a compatible image.

#### Create a model deployment
- Open Practicus AI management console > ML Model Hosting > Model Deployments
- Add a new model deployment with GPUs, selecting the custom image you created above.
- Set the below os environment variables using the `Extra configuration` section:
- `PRT_SERVE_MODEL`: Hugging Face model ID
- `PRT_SERVE_MODEL_OPTIONS_B64`: (optional) Base64‑encoded JSON of VLLM options

#### Create models
- Open Practicus AI management console > ML Model Hosting > Models
- Add a `new model` e.g. `my-tiny-model`
- Add a `new version` to this model and point to the model deployment you created above.
- Tip: You can create `multiple versions` each pointing to different model deployments, and then perform `A/B testing` comparing LLM model performance.


**Example 1**: Serving TinyLlama

Add the below to model deployment in `Extra configuration` section
```
PRT_SERVE_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

**Example 2**: Serving with customized options, e.g. for smaller GPUs like Nvidia T4.

- Create base64 encoded options json, run on your terminal the below:
```bash
echo '{"dtype": "half"}' | base64
# prints eyJkdHlwZSI6ICJoYWxmIn0K
```

- Add the below to model deployment in `Extra configuration` section
```
PRT_SERVE_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
PRT_SERVE_MODEL_OPTIONS_B64=eyJkdHlwZSI6ICJoYWxmIn0K
```


<!-- #endregion -->

### Option 2: Pre-download model files and save to container image (recommended)

You can bake the model into your image to avoid runtime downloads. This is `strongly recommended` for production models.

```dockerfile
FROM ghcr.io/practicusai/practicus-modelhost-base-gpu-vllm:25.5.0

# Let's pick a tiny, yet effective model.
ENV PRT_SERVE_MODEL="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Let's assume this model runs on small/legacy GPU e.g. Nvidia T4
# Generated running:
#   echo '{"dtype": "half"}' | base64
ENV PRT_SERVE_MODEL_OPTIONS_B64="eyJkdHlwZSI6ICJoYWxmIn0K"

# Change model download path from the default ~/.cache/huggingface since the container image can run
# with a different user than the one in build time.
ENV HF_HOME="/var/practicus/cache/huggingface"

RUN \
    # Download model for offline use
    echo "Starting to download '$PRT_SERVE_MODEL' to '$HF_HOME'." && \
    mkdir -p "$HF_HOME" && \
    huggingface-cli download "$PRT_SERVE_MODEL" --local-dir "$HF_HOME" && \
    echo "Completed downloading '$PRT_SERVE_MODEL' to '$HF_HOME'." && \
    # Create VLLM redirect file
    REDIRECT_JSON="{\"$PRT_SERVE_MODEL\": \"$HF_HOME\"}" && \
    REDIRECT_JSON_PATH="/var/practicus/vllm_model_redirect.json" && \
    echo "Creating VLLM redirect file: $REDIRECT_JSON_PATH" && \
    echo "VLLM redirect JSON content: $REDIRECT_JSON" && \
    echo "$REDIRECT_JSON" > "$REDIRECT_JSON_PATH"

# Use VLLM redirect file for downloaded model
ENV VLLM_MODEL_REDIRECT_PATH="/var/practicus/vllm_model_redirect.json"


COPY  model.py /var/practicus/model.py
# (Recommended) Enable Offline mode to prevent accidentally downloading missing models in run-time.
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1
```



### Option 3: Custom `model.py` implementation

You can save `/var/practicus/model.py` to your custom container image to customize the init and serving steps.

```python
# /var/practicus/model.py
import practicuscore as prt


async def init(**kwargs):
    if not prt.models.server.initialized:
        prt.models.server.start()


async def serve(http_request, payload: dict, **kwargs):
    return await prt.models.server.serve(http_request=http_request, payload=payload, **kwargs)

```

## Experimenting in Design Time

You can interactively start, chat, and stop from within a Practicus AI Worker Jupyter Notebook.

```python
from openai import OpenAI
import practicuscore as prt

# Start and wait until ready
prt.models.server.start("TinyLlama/TinyLlama-1.1B-Chat-v1.0", options={"dtype": "half"})

base_url = prt.models.server.get_base_url() + "/v1"
print("Model URL:", base_url)
# prints http://localhost:8585/v1

# Create OpenAI client
client = OpenAI(
    base_url=base_url,
    # Token not needed for local use
    api_key="not-needed",
)

# Send a chat request
response = client.chat.completions.create(
    # Select the model you just downloaded.
    # Tip: To always use the current model you can set model=None
    model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    messages=[{"role": "user", "content": "Capital of France?"}],
    max_tokens=100,
)
print(response.choices[0].message.content)
#  Prints 'Paris'
```

#### Additional Utilities

- `prt.models.server.get_status()` → check `running`, `error`, etc.
- `prt.models.server.get_output()` → recent logs
- `prt.models.server.stop()` → stop the server


```python
print("Status:", prt.models.server.get_status())
print("Logs:\n", prt.models.server.get_output())
```

### Testing with a Mock LLM Server on CPU
Point to a CPU‑only mock server. See the sample file `mock_llm_server.py`

```python
# Start the mock server
prt.models.server.start("mock_llm_server.py")

base_url = prt.models.server.get_base_url()

# Send a mock request
client = OpenAI(base_url=base_url, api_key="not-needed")
response = client.chat.completions.create(model="mock_llm", messages=[{"role": "user", "content": "Hello mock!"}])

print(response.choices[0].message.content)
# Prints Hello mock!
```

#### Cleaning Up

Stop the server when you're done:


```python
prt.models.server.stop()
```


## Supplementary Files

### mock_llm_server.py
```python
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


@app.post("/chat/completions")
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

```


---

**Previous**: [Build](../../apps/build.md) | **Next**: [Custom > Models > Build](../custom/models/build.md)
