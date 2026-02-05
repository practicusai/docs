---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Practicus AI MCP Gateway

This example shows how to configure LiteLLM's MCP Gateway features using in Practicus AI,

## What you get
- Define MCP servers in Python (`GatewayMcpServer`)
- Attach them to `GatewayConfig`
- Start gateway with `ModelServer.start_gateway(config=...)`
- LiteLLM runs with a generated YAML
- For more information on MCP gateway configuration, please visit <https://docs.litellm.ai/docs/mcp>



## Build a GatewayConfig with MCP servers

Below is the minimal shape:
- `models`: your normal LiteLLM model list (can be empty if you only want MCP, if your validator allows)
- `mcp_servers`: list of MCP servers
- `mcp_aliases`: optional alias mapping for client headers
- `enable_mcp_registry`: optional to serve a registry endpoint


```python
# Sample model.py
import os
import practicuscore as prt

# Example token (do NOT hardcode in production)
demo_token = "demo_bearer_token_value"

mcp_server = prt.GatewayMcpServer(
    name="my-mcp",
    transport="sse",
    url="https://mcp.example.com/mcp",
    auth_type="bearer_token",
    auth_value=demo_token,
    # Optional filtering
    allowed_tools=["search", "lookup"],
)

# Token from OS env
os.environ["MY_MCP_TOKEN"] = "demo_token_from_env"

mcp_server_env = prt.GatewayMcpServer(
    name="my-mcp-env",
    transport="sse",
    url="https://mcp.example.com/mcp",
    auth_type="bearer_token",
    auth_value_os_env="MY_MCP_TOKEN",
)


# Minimal example model (adjust to your real models)
# model = GatewayModel(
#     name="practicus/demo",
#     model="openai/gpt-4o-mini",
#     api_key_os_env="OPENAI_API_KEY",
# )

gateway_conf = prt.GatewayConfig(
    models=[],  # replace with [model] in real usage
    mcp_servers=[
        mcp_server,
        mcp_server_env,
    ],
    mcp_aliases={
        # Client may send x-mcp-servers: alias1,alias2
        # and LiteLLM maps alias -> server name
        "alias_my": "my-mcp-env",
    },
)


async def init(**kwargs):
    prt.models.server.start_gateway(config=gateway_conf)


async def serve(**kwargs):
    return await prt.models.server.serve(**kwargs)

```

## How to use your MCP servers

Once the configuration is completed, deploy your model as usual.

```python
import practicuscore as prt

deployment_key = None  # E.g. "my-model-depl-for-litellm"
prefix = "models"
model_name = "litellm-proxy"

assert deployment_key

api_url, api_version_url, api_meta_url = prt.models.deploy(
    deployment_key=deployment_key,
    prefix=prefix,
    model_name=model_name,
)
```

And your mcp server(s) should be accessible from a URL like `https://practicus.company.com/models/litellm-proxy/mcp/`

You can also use a specific version. E.g `http://local.practicus.io/models/litellm-proxy/v3/mcp/` or standard version tags `latest` `prod` `staging` like `http://local.practicus.io/models/litellm-proxy/prod/mcp/`. 

Please note that version tags must come before the `/mcp/` part


---

**Previous**: [Guardrails And Policies](guardrails-and-policies.md) | **Next**: [Custom > Models > Build](../custom/models/build.md)
