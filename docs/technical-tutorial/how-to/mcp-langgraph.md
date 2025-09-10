---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus GenAI
    language: python
    name: practicus_genai
---

# Using Practicus AI MCP Servers with LangGraph

```python
# E.g. "https://practicus.my-company.com/apps/agentic-ai-test/api/sys/mcp/"
agentic_test_mcp_url = None 
# Api token for the MCP server. You can also get dynamic using SDK.
api_token = None
# OpenAI or compatible LLM API key
open_ai_key = None
```

```python
assert agentic_test_mcp_url, "MCP Server URL is not defined"
assert api_token, "API token for MCP server not defined"
```

```python
if not open_ai_key:
    import os
    import getpass
    
    open_ai_key = getpass.getpass("Enter key for OpenAI or an OpenAI compatible Practicus AI LLM: ")

os.environ["OPENAI_API_KEY"] = open_ai_key

assert os.environ["OPENAI_API_KEY"], "OpenAI key is not defined"
```

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)
```

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

client = MultiServerMCPClient(
    {
        "agentic_test": {
            "url": agentic_test_mcp_url,
            "transport": "streamable_http",
            "headers": {
                "Authorization": f"Bearer {api_token}",
            },
            
        }
    }
)
tools = await client.get_tools()

for tool in tools:
    print(f"Located tool:\n{tool}\n")

```

```python
agent = create_react_agent(
    llm,
    tools
)

request = "Hi, I'd like to place an order. I'm ordering 2 Widgets priced at $19.99 each and 1 Gadget priced at $29.99. Could you please process my order, generate a detailed receipt, and then send me a confirmation message with the receipt details?"
print(f"Sending request to LLM:\n{request}")

test_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": request}]}
)

print("Received response:")
print(test_response)
```


---

**Previous**: [Personal Startup Scripts](personal-startup-scripts.md) | **Next**: [Extras > Modeling > SparkML > Ice Cream > SparkML Ice Cream](../extras/modeling/sparkml/ice-cream/sparkml-ice-cream.md)
