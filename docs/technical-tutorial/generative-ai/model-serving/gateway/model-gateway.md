---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Practicus AI Model Gateway for LLMs

This document explains how to leverage the Practicus AI platform’s optimized Large Language Model (LLM) gateway features, powered by high-performance inference engines such as **LiteLLM**, and others. The Practicus AI Model Gateway serves as a unified proxy layer, enabling seamless management and deployment of LLMs—whether hosted on Practicus AI or accessed via third-party services.

Whether you're using **Practicus AI's optimized vLLM hosting**, third-party services like **OpenAI**, or even your own **custom inference code**, the Gateway provides a single, consistent interface. This notebook will guide you through the entire process, from basic configuration to advanced dynamic routing and security guardrails.

The following sections will guide you through key aspects of the Model Gateway, including initial setup, configuration, advanced features, and deployment.

## Contents

1. **Core Concepts**
   Overview of the primary configuration objects used by the Model Gateway.

2. **Configuration Strategies**
   Options for defining Gateway behavior using Python code, YAML files, or hybrid approaches.

3. **Logging and Cost Tracking**
   How to connect a database for comprehensive monitoring of usage and spend.

4. **Advanced Customization**
   Implementation of hooks, security guardrails, and dynamic routing for production workloads.

5. **Deployment**
   Steps to launch your Gateway configuration on the Practicus AI platform.


## 1. Core Concepts: The Configuration Trio

Your model Gateway setup is defined by Python (pydantic) objects declared in a single file, typically named `model.py`. Practicus AI automatically handles the complex backend work, like generating the necessary `litellm_config.yaml` and attaching your custom functions.

There are three Pydantic classes you'll use:

- **`GatewayModel`**: Defines a single model endpoint. This is what your users will call. It can be a concrete model (e.g., `openai/gpt-4o`) or a *virtual router* that intelligently delegates requests to other models.

- **`GatewayGuardrail`**: A reusable, gateway-wide security or transformation rule. Guardrails can be applied to all models by default or selectively enabled by clients on a per-request basis.

- **`GatewayConfig`**: The root object that brings everything together. It holds the list of all your models and guardrails, along with global settings like database connections.


## 2. Configuration Strategies

The Gateway offers flexible configuration options to fit your workflow. The recommended approach is to define your configuration in Python, as it provides the most power and flexibility, especially when using custom logic like routers and hooks.


### 2.1. The `model.py` File: Your Gateway's Blueprint

When you deploy a Gateway, the Practicus AI platform looks for a `model.py` file. This file must contain two key async functions:
- **`init(**kwargs)`**: This function is executed once when your model server starts. It's the perfect place to initialize your Gateway configuration and start the server using `prt.models.server.start_gateway()`.
- **`serve(**kwargs)`**: This function is called for every incoming request. You'll typically just pass the request through to the running Gateway server with `await prt.models.server.serve(**kwargs)`.

```python
import practicuscore as prt
import os

# Step 1: Define your models using the GatewayModel class

# An OpenAI model, with the API key read from an environment variable
model_gpt_4o = prt.GatewayModel(
    name="practicus/gpt-4o",
    model="openai/gpt-4o",
    api_key_os_env="OPENAI_API_KEY",
)

# A model hosted on Practicus AI's vLLM service
# Note: For Practicus AI hosted models, if user impersonation is enabled,
# you can omit the api_key, and a dynamic token will be generated.
model_hosted_vllm = prt.GatewayModel(
    name="practicus/my-hosted-llama",
    model="hosted_vllm/my-llama-3-deployment",
    api_base="http://local.practicus.io/models/open-ai-proxy/",  # The internal URL to the deployment
    api_key_os_env="MY_VLLM_TOKEN",  # The service account token for the deployment
)

# Step 2: Create the main GatewayConfig object
gateway_conf = prt.GatewayConfig(
    models=[
        model_gpt_4o,
        model_hosted_vllm,
    ],
    strict=False,  # If True, configuration errors will block requests
)

# Step 3: Implement the init and serve functions


async def init(**kwargs):
    """Initializes and starts the Gateway server."""

    # It's best practice to set secrets from a secure source like Practicus Vault
    os.environ["OPENAI_API_KEY"] = "sk-...."
    os.environ["MY_VLLM_TOKEN"] = "eyJh..."

    # Start the gateway with our configuration
    # The `module` path is detected automatically
    prt.models.server.start_gateway(config=gateway_conf)


async def serve(**kwargs):
    """Handles incoming inference requests."""
    return await prt.models.server.serve(**kwargs)
```

### 2.2. Using an External LiteLLM YAML (`custom_conf`)

If your model gateway inference engine is LiteLLM (default) and have an existing `litellm_config.yaml` or prefer a pure YAML setup, you can use the `custom_conf` argument. The Gateway will use this as a base configuration.

You can provide it as a raw string or a file path. This can be combined with a Python-based `GatewayConfig` object; settings in the Python object will **override** any conflicting settings in the YAML.

```python
# Example of a hybrid configuration

# Base configuration in a YAML string
custom_yaml_config = """
model_list:
  - model_name: practicus/claude-3-sonnet
    litellm_params:
      model: claude-3-sonnet-20240229
      api_key: "[ANTHROPIC_API_KEY]"
"""

# Python GatewayModel to add to the config
model_gpt_4o_with_cost = prt.GatewayModel(
    name="practicus/gpt-4o",
    model="openai/gpt-4o",
    api_key_os_env="OPENAI_API_KEY",
    input_cost_per_token=0.000005,  # $5 / 1M tokens
    output_cost_per_token=0.000015,  # $15 / 1M tokens
)

# The final config merges both. The gateway will serve both
# 'practicus/claude-3-sonnet' (from YAML) and 'practicus/gpt-4o' (from code).
gateway_conf_hybrid = prt.GatewayConfig(
    custom_conf=custom_yaml_config,
    models=[
        model_gpt_4o_with_cost,
    ],
)

# You would then use `gateway_conf_hybrid` in your init function.
```

<!-- #region -->
## 3. Database Logging & Cost Tracking

To enable detailed logging of requests, responses, usage, and spend, you can connect the Gateway to a PostgreSQL database. 

#### Cost Tracking
Set the `input_cost_per_token` and `output_cost_per_token` on any `GatewayModel` to automatically calculate and log the cost of each API call. This is invaluable for monitoring expenses and billing users.

#### Database Setup
Provide a standard PostgreSQL connection string to the `database_url` parameter in your `GatewayConfig`.

```python
gateway_conf = prt.GatewayConfig(
    # ... other settings
    database_url="postgresql://user:password@db_host:port/db_name"
)
```

**🚨 IMPORTANT 🚨**
Before the Gateway runs for the first time with a new database, the schema must be created. To do this, you must set the following environment variable in your Practicus AI Model Deployment's `Extra configuration` section:

```text
USE_PRISMA_MIGRATE=True
```

The server will perform the migration on startup and then exit. You should **remove this variable** after the first successful run to prevent migration attempts on every restart.

> For details on the database schema, see the official LiteLLM documentation: [schema.prisma](https://github.com/BerriAI/litellm/blob/main/schema.prisma)
<!-- #endregion -->

## 4. Advanced Customization: Hooks, Guards, and Routers

The true power of the Gateway lies in its extensibility. You can inject custom asynchronous Python code at various points in the request/response lifecycle. All hook functions must be defined in the same `model.py` file.


### 4.1. Model-Specific Hooks

You can attach callbacks directly to a `GatewayModel` to execute logic only for that model. 

- **`pre_guards` & `post_guards`**: Lists of async functions that can inspect or *modify* the request payload (pre) or response object (post).
- **`pre_call`**: A single async function that runs just before the call to the LLM, after routing.
- **`post_call_success` & `post_call_failure`**: Async functions for side effects like logging or metrics after a successful or failed LLM call.

```python
import practicuscore as prt


# Example of a pre-guard hook to add metadata to the request
async def add_custom_metadata(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """This hook inspects the request and adds metadata."""
    # Add a custom tracking ID to the request payload
    if "metadata" not in data:
        data["metadata"] = {}
    data["metadata"]["gateway_tracking_id"] = "gtw-12345"

    # Note: kwargs can have other relevant info

    # You MUST return the modified data dictionary
    return data


# Example of a post-call hook for logging
async def log_successful_call(data: dict, response, requester: dict | None = None, **kwargs):
    """This hook runs after a successful call."""
    print(f"Responding: {response}")
    # ... add custom logging logic here ...
    # 'data' has user request.
    # 'response' has llm response, including token usage.
    # Note: kwargs can have other relevant info


# Apply the hooks to a GatewayModel
model_with_hooks = prt.GatewayModel(
    name="practicus/gpt-4o-guarded",
    model="openai/gpt-4o",
    api_key_os_env="OPENAI_API_KEY",
    pre_guards=[add_custom_metadata],  # Can also pass the function name as a string: "add_custom_metadata"
    post_call_success=log_successful_call,
)
```

### 4.2. Dynamic Routing

Dynamic routing allows you to create a *virtual* model that decides which *concrete* model to use at runtime based on custom logic. To create a router, define a `GatewayModel` but provide a `router` function instead of a `model` identifier.

Your router function will receive the request data and must return the `name` of the `GatewayModel` to forward the request to (e.g., `"practicus/gpt-4o"`).

#### Routing Based on Metrics
A common use case is to route based on performance metrics like latency or token throughput. You can fetch these using `prt.models.server.gateway_stats()`.

⚠️ **The Chicken-and-Egg Problem:** The `gateway_stats` are collected *locally* on each gateway replica. A model will have no stats until it receives traffic. Your router logic **must** include a fallback/default model to handle cases where stats are not yet available. This ensures that new or underutilized models eventually get traffic and generate the metrics needed for routing.

**Advanced Strategies:**
- For robustness, wrap your routing logic in a `try...except` block to always return a fallback model.
- For global routing decisions across all replicas, consider pulling aggregated metrics from a central monitoring system like Prometheus within your router function.

```python
import practicuscore as prt

# First, define the concrete models that our router can choose from
model_fast = prt.GatewayModel(
    name="practicus/fast-model",
    model="groq/llama3-8b-8192",  # A known fast model
    api_key_os_env="GROQ_API_KEY",
)

model_powerful = prt.GatewayModel(
    name="practicus/powerful-model",
    model="openai/gpt-4o",  # A known powerful model
    api_key_os_env="OPENAI_API_KEY",
)


# Now, define the router function
async def intelligent_router(data: dict, **kwargs) -> str:
    """Routes to a fast model for short prompts, and a powerful one for long prompts."""
    user_prompt = data.get("messages", [{}])[-1].get("content", "")

    # Simple logic: if prompt is short, use the fast model.
    if len(user_prompt) < 200:
        print("Routing to FAST model")
        return model_fast.name  # Return the name of the target model

    # Otherwise, use the powerful model
    print("Routing to POWERFUL model")
    return model_powerful.name


# Finally, define the virtual model that uses the router
model_intelligent_router = prt.GatewayModel(
    name="practicus/intelligent-router",  # This is the name clients will call
    router=intelligent_router,  # Assign the router function
)
```

### 4.3. Gateway-Level Guardrails

A `GatewayGuardrail` is a hook that can be applied across the entire gateway. This is useful for enforcing broad policies like PII scrubbing or content moderation.

- **`default_on=True`**: The guardrail is automatically applied to **all models, all the time**. Use this with extreme caution.
- **`default_on=False`**: The guardrail is available, but inactive. Clients must explicitly request it in their API call by passing its name in the `extra_body`.

```python
import practicuscore as prt
from pathlib import Path
from openai import OpenAI


# Define a guardrail function
async def pii_scrubber(data: dict, **kwargs) -> dict:
    """A simple PII scrubber that replaces email addresses."""
    for message in data.get("messages", []):
        content = message.get("content", "")
        # This is a naive example; use a proper library in production!
        message["content"] = content.replace("test@example.com", "[REDACTED_EMAIL]")
    return data


# Create a GatewayGuardrail instance for it
pii_guard = prt.GatewayGuardrail(
    name="pii-scrubber",
    mode="pre_call",  # This runs before the LLM call
    guard=pii_scrubber,
    default_on=False,  # It is OFF by default
)

# This guardrail would then be added to the GatewayConfig:
# Optional: you can pass the path of the python file that has the guardrail function, e.g. pii_scrubber
#   If left empty, .py file location is auto detected.
# module_path = str(Path(__file__).resolve())
# gateway_conf = prt.GatewayConfig(
#     models=[...],
#     guardrails=[pii_guard],
#     module=module_path,
# )

# --- Client-Side Usage ---
# To activate the guardrail, a client would make a call like this:

# client = OpenAI(base_url=...)
# response = client.chat.completions.create(
#     model="practicus/gpt-4o",
#     messages=[{"role": "user", "content": "My email is test@example.com"}],
#     extra_body={
#         "guardrails": ["pii-scrubber"] # Requesting the guardrail by name
#     },
# )
```

<!-- #region -->
## 5. User Context and Impersonation

All custom functions (hooks, routers, guards) receive a `requester` dictionary in their `**kwargs`. This object contains valuable information about the authenticated user making the API call, such as their ID, roles, and other metadata provided by the Practicus AI platform.

```python
async def my_hook(data: dict, requester: dict | None, **kwargs):
    if requester:
        print(f"Request made by user ID: {requester.get('id')}")
```

This enables powerful features like per-user validation, dynamic API key generation for Practicus-hosted models, or custom routing based on user roles.

#### Debugging with `PRT_OVERWRITE_GATEWAY_REQUESTER`

For local development and testing, it can be difficult to simulate different users. To solve this, you can set the `PRT_OVERWRITE_GATEWAY_REQUESTER` environment variable. Set its value to a JSON string representing the `requester` object you want to simulate. The Gateway will use this mock object for all incoming calls, allowing you to easily test logic that depends on user context.
<!-- #endregion -->

## 6. Deployment

Once your `model.py` is ready, deploying it is straightforward. You place the file in your project directory and use the standard `prt.models.deploy()` function from within a Practicus AI notebook.

The platform will automatically package your `model.py` and its dependencies, create a dedicated Model Deployment on Kubernetes, and expose it as a secure, scalable API endpoint.

Behind the scenes, the deployment's container will:
1. Start up.
2. Execute your `init()` function.
3. Your `init()` function calls `prt.models.server.start_gateway(config=...)`, which launches the LiteLLM proxy with the configuration you defined.
4. The endpoint is now live and ready to handle requests via your `serve()` function.

```python
import practicuscore as prt

# Ensure your model.py file (containing your GatewayConfig, hooks, init, and serve)
# is in the project's root directory or a specified subdirectory.

deployment_key = None  # E.g. "my-gateway-deployment" a unique name for the K8s deployment
prefix = "models"  # The API path prefix
model_name = "llm-gateway"  # The name of your model in Practicus AI

if deployment_key:
    api_url, api_version_url, api_meta_url = prt.models.deploy(
        deployment_key=deployment_key,
        prefix=prefix,
        model_name=model_name,
    )

    print(f"Deployment initiated. API will be available at: {api_url}")
```

## 7. Conclusion

The Practicus AI Model Gateway provides a powerful, flexible, and unified way to manage all of your LLM endpoints. By leveraging Python-based configuration, you can move beyond simple proxying and build sophisticated applications with features like:

- ✅ **Centralized Model Catalog:** A single point of access for all your models.
- ✅ **Cost and Usage Monitoring:** Detailed logs for chargebacks and analysis.
- ✅ **Intelligent Routing:** Optimize for cost, latency, or performance by dynamically selecting the best model for the job.
- ✅ **Robust Security:** Implement custom guardrails to enforce policies across all requests.

This notebook provides the foundation for you to get started. Don't hesitate to explore the Pydantic class definitions for a full list of available parameters and build the exact LLM gateway your organization needs.


---

**Previous**: [Model Serving](../llm/model-serving.md) | **Next**: [Guardrails And Policies](guardrails-and-policies.md)
