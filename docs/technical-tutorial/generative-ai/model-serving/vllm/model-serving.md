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

# Practicus AI Large Language Model (LLM) Hosting

This example demonstrates how to leverage the Practicus AI platform's optimized LLM hosting features, powered by engines like vLLM for high-throughput and low-latency inference. We will cover:

1.  **Experimenting in Design Time:** Interactively running and testing LLMs directly within a Practicus AI Worker's Jupyter environment using the `ModelServer` utility.
2.  **Deploying for Runtime:** Packaging and deploying LLMs as scalable endpoints on the Practicus AI Model Hosting platform.

This approach is the recommended method for hosting most Large Language Models on Practicus AI, offering significant performance benefits and simplified deployment compared to writing custom prediction code from scratch.

> **Note:** If you need to host non-LLM models or require deep customization beyond the options provided by the built-in LLM serving engine (e.g., complex pre/post-processing logic tightly coupled with the model), please view the custom model serving section for guidance on building models with custom Python code.


## 1. Overview of the `prt.models.server` Utility

The `practicuscore.models.server` module (`prt.models.server`) provides a high-level interface to manage LLM inference servers within the Practicus AI environment. Primarily, it controls an underlying inference engine process (like vLLM by default) and exposes its functionality.

Key capabilities include:

* **Starting/Stopping Servers:** Easily launch and terminate the inference server process (e.g., vLLM) with specified models and configurations (like quantization, tensor parallelism).
* **Health & Status Monitoring:** Check if the server is running, view logs, and diagnose issues.
* **Providing Access URL:** Get the local URL to interact with the running server.
* **Runtime Integration:** Facilitates deploying models using optimized container images, often exposing an OpenAI-compatible API endpoint for standardized interaction.


## 2. Experimenting in Design Time (Jupyter Notebook)

You can interactively start an LLM server, send requests, and shut it down directly within a Practicus AI Worker notebook. This is ideal for development, testing prompts, and evaluating different models or configurations before deployment.

**Note:** This runs the server *locally* within your Worker's resources. Ensure your Worker has sufficient resources (especially GPU memory) for the chosen model.

```python
import practicuscore as prt
from openai import OpenAI
import time

# Define the model from Hugging Face and any specific engine options
# Example: Use TinyLlama and specify 'half' precision (float16) suitable for GPUs like T4
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
vllm_options = {"dtype": "half"}

# Start the vLLM server process and wait for it to become ready
print(f"Starting server for model: {model_id} with options: {vllm_options}...")
prt.models.server.start(model_id, options=vllm_options)

# The server might take a moment to initialize, especially on first download

# Get the base URL of the locally running server
# Append '/v1' for the OpenAI-compatible API endpoint
base_url = prt.models.server.get_base_url()
if not base_url:
    print("Error: Server failed to start. Check logs:")
    print(prt.models.server.get_output())
else:
    openai_api_base = base_url + "/v1"
    print(f"Server started. OpenAI compatible API Base URL: {openai_api_base}")

    # Create an OpenAI client pointed at the local server
    # No API key is needed ('api_key' can be anything) for local interaction
    client = OpenAI(
        base_url=openai_api_base,
        api_key="not-needed-for-local",
    )

    # Send a chat completion request
    print("Sending chat request...")
    try:
        response = client.chat.completions.create(
            # The 'model' parameter should match the model loaded by the server
            # You can often use model=None if only one model is served, 
            # or explicitly pass the model_id
            model=model_id, 
            messages=[{"role": "user", "content": "What is the capital of France?"}],
            max_tokens=50, # Limit response length
            temperature=0.7
        )
        print("Response received:")
        print(response.choices[0].message.content)
        # Expected output might be similar to: 'The capital of France is Paris.'
    except Exception as e:
        print(f"Error during chat completion: {e}")
        print("Check server status and logs.")

```

### Additional Utilities for Design Time

While the server is running in your notebook session, you can monitor it:

```python
# Check the server's status ('running', 'error', 'stopped', etc.)
status = prt.models.server.get_status()
print(f"Server Status: {status}")

# Get recent logs (stdout/stderr) from the server process
logs = prt.models.server.get_output()
print("Recent Server Logs:")
print(logs)
```

### Testing with a Mock LLM Server on CPU

For testing pipelines or developing client code without requiring a GPU or a real LLM, you can run a simple mock server. This mock server just needs to implement the expected API endpoint (e.g., `/v1/chat/completions`).

Create a Python file (view example `mock_llm_server.py` at the bottom of this page) with a basic web server (like Flask or FastAPI) that returns predefined responses. Then, start it using `prt.models.server.start()`.

```python
# Example: Assuming you have 'mock_llm_server.py' in the same directory
# This file would contain a simple Flask/FastAPI app mimicking the OpenAI API structure
try:
    print("Attempting to stop any existing server...")
    prt.models.server.stop() # Stop the real LLM server if it's running
    time.sleep(2)

    print("Starting the mock server...")
    # Make sure 'mock_llm_server.py' exists and is runnable
    prt.models.server.start("mock_llm_server.py") 
    time.sleep(5) # Give mock server time to start

    mock_base_url = prt.models.server.get_base_url()
    if not mock_base_url:
        print("Error: Mock server failed to start. Check logs:")
        print(prt.models.server.get_output())
    else:
        mock_api_base = mock_base_url + "/v1"
        print(f"Mock Server Running. API Base: {mock_api_base}")

        # Create client for the mock server
        mock_client = OpenAI(base_url=mock_api_base, api_key="not-needed")

        # Send a request to the mock server
        mock_response = mock_client.chat.completions.create(
            model="mock-model", # Model name expected by your mock server
            messages=[{"role": "user", "content": "Hello mock!"}]
            )
        print("Mock Response:", mock_response.choices[0].message.content)
        # Example mock server might return: 'You said: Hello mock!'
except FileNotFoundError:
    print("Skipping mock server test: 'mock_llm_server.py' not found.")
except Exception as e:
    print(f"An error occurred during mock server test: {e}")
finally:
    # Important: Stop the mock server when done
    print("Stopping the mock server...")
    prt.models.server.stop()
```

### Cleaning Up the Design Time Server

When you are finished experimenting in the notebook, **it's crucial to stop the server** to release GPU resources.

```python
print("Stopping any running server...")
prt.models.server.stop()
print(f"Server Status after stop: {prt.models.server.get_status()}")
```

## 3. Deploying Models for Runtime

Once you have selected and tested your model, you need to deploy it as a scalable service on the Practicus AI Model Hosting platform. This involves packaging the model and its serving configuration into a container image and creating a deployment through the Practicus AI console.

There are a few ways to configure the container for LLM serving:


### Option 1: Dynamically Download Model at Runtime (No Coding Required)

This is the quickest way to get started. Use a pre-built Practicus AI vLLM image, and configure the model ID and options via environment variables in the model deployment settings. The container will download the specified model when it starts.

**Pros:** Simple configuration, no need to build custom images.
**Cons:** Can lead to longer cold start times as the model needs to be downloaded on pod startup. Potential for download issues at runtime.

**Steps:**

1.  **Define Container Image in Practicus AI:**
    * Navigate to `Infrastructure > Container Images` in the Practicus AI console.
    * Add a new image. Use a vLLM-enabled image provided by Practicus AI, for example: `ghcr.io/practicusai/practicus-modelhost-gpu-vllm:25.5.0` (replace with the latest/appropriate version).

2.  **Create Model Deployment:**
    * Go to `ML Model Hosting > Model Deployments`.
    * Create a new deployment, ensuring you allocate necessary GPU resources.
    * Select the container image you added in the previous step.
    * In the `Extra configuration` section (or environment variables section), define:
        * `PRT_SERVE_MODEL`: Set this to the Hugging Face model ID (e.g., `TinyLlama/TinyLlama-1.1B-Chat-v1.0`).
        * `PRT_SERVE_MODEL_OPTIONS_B64`: (Optional) Provide Base64-encoded JSON containing vLLM options (like `{"dtype": "half"}`).

3.  **Create Model and Version:**
    * Go to `ML Model Hosting > Models`.
    * Add a `New Model` (e.g., `my-tiny-llama`).
    * Add a `New Version` for this model, pointing it to the `Model Deployment` you just created.
    * Tip: You can create `multiple versions` each pointing to different model deployments, and then perform `A/B testing` comparing LLM model performance.

**Example 1: Serving TinyLlama (default options)**

In Model Deployment `Extra configuration` section, add:

```text
PRT_SERVE_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

**Example 2: Serving TinyLlama with Half Precision**

* Generate Base64 options:
  
    ```bash
    # On your local machine or a terminal:
    echo '{"dtype": "half"}' | base64
    # Prints eyJkdHlwZSI6ICJoYWxmIn0K
    
    ```
    
* In Model Deployment `Extra configuration` section, add:
  
    ```text
    PRT_SERVE_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
    PRT_SERVE_MODEL_OPTIONS_B64=eyJkdHlwZSI6ICJoYWxmIn0K
    ```


### Option 2: Pre-download and Bake Model into Container Image (Recommended for Production)

Build a custom container image that includes the model files. This avoids runtime downloads, leading to faster and more reliable pod startups.

**Pros:** Faster cold starts, improved reliability (no runtime download dependency), enables offline environments.
**Cons:** Requires building and managing custom container images. Image size will be larger. Longer build times.

**Steps:**

1.  **Create a `Dockerfile`:**
    * Start from a Practicus AI base vLLM image.
    * Set environment variables for the model and options.
    * Use `huggingface-cli download` to download the model during the image build.
    * (Optional but recommended) Configure vLLM to use the downloaded path and enable offline mode.
    * (Optional) If you need custom logic, `COPY` your `model.py` (see Option 3).

2.  **Build and Push the Image:** Build the Docker image and push it to a container registry accessible by Practicus AI.

3.  **Configure Practicus AI:**
    * Add your custom image URL in `Infrastructure > Container Images`.
    * Create a `Model Deployment` using your custom image. You usually *don't* need to set `PRT_SERVE_MODEL` or `PRT_SERVE_MODEL_OPTIONS_B64` as environment variables here, as they are baked into the image (unless your image startup script specifically reads them).
    * Create the `Model` and `Version` pointing to this deployment.


**Example `Dockerfile`:**

```dockerfile
# Use a Practicus AI base image that includes GPU support and vLLM
FROM ghcr.io/practicusai/practicus-modelhost-base-gpu-vllm:25.5.0

# --- Configuration baked into the image ---
ENV PRT_SERVE_MODEL="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Example: Options for smaller GPUs like Nvidia T4 (float16)
# Generated via: echo '{"dtype": "half"}' | base64
ENV PRT_SERVE_MODEL_OPTIONS_B64="eyJkdHlwZSI6ICJoYWxmIn0K"

# --- Model Download during Build ---
# Define a persistent cache location within the image
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

# --- vLLM Configuration for Baked Model ---
# Tell vLLM (via our entrypoint) to use the baked model path directly
ENV VLLM_MODEL_REDIRECT_PATH="/var/practicus/vllm_model_redirect.json"

# (Recommended for baked images) Prevent accidental downloads at runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

# --- Custom Logic (Optional - See Option 3) ---
# If you need custom init/serve logic, uncomment and provide your model.py
# COPY model.py /var/practicus/model.py
```


### Option 3: Custom `model.py` Implementation

If you need to add custom logic before or after the vLLM server handles requests (e.g., complex input validation/transformation, custom readiness checks, integrating external calls), you can provide a `/var/practicus/model.py` file within your custom container image (usually built as described in Option 2).

**Pros:** Maximum flexibility for custom logic around the vLLM server.
**Cons:** Requires Python coding; adds complexity compared to standard vLLM usage.

**Steps:**

1.  Create your `model.py` with `init` and `serve` functions.
2.  Inside `init`, call `prt.models.server.start()` to launch the vLLM process.
3.  Inside `serve`, you can add pre-processing logic, then call `await prt.models.server.serve()` to forward the request to the underlying vLLM server, and potentially add post-processing logic to the response.
4.  Build a custom Docker image (as in Option 2), ensuring you `COPY model.py /var/practicus/model.py`.

```python
# Example: /var/practicus/model.py 
# Customize as required and place  in your project and COPY into the Docker image
import practicuscore as prt


async def init(**kwargs):
    if not prt.models.server.initialized:
        prt.models.server.start()


async def serve(http_request, payload: dict, **kwargs):
    return await prt.models.server.serve(http_request=http_request, payload=payload, **kwargs)

```

## 4. Conclusion

Practicus AI provides optimized pathways for hosting LLMs using engines like vLLM.

* Use the `prt.models.server` utility within notebooks for **interactive experimentation**.
* For **runtime deployment**, choose between dynamic model downloads (easy start) or baking models into images (recommended for production) via the Practicus AI console.
* Use a custom `model.py` only when specific pre/post-processing logic around the core LLM inference is required.

Remember to consult the specific documentation for vLLM options and Practicus AI deployment configurations for advanced settings.


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
