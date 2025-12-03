---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Dynamically Accessing AI Assistant Metadata

Instead of manually configuring AI Assistant URLs, you can use the Practicus AI SDK to dynamically fetch available AI Assistants associated with your user account.

```python
import json
import practicuscore as prt
```

```python
region = prt.current_region()
ai_assistants = region.get_ai_assistants()
```

```python
print("Available AI Assistants:")
for assistant in ai_assistants:
    print(json.dumps(assistant, indent=4))
```

### Example: Selecting the First AI Assistant

```python
selected_ai_assistant = ai_assistants[0]
```

```python
from practicuscore.gen_ai import AIAssistantHelper
```

```python
assistant_url = AIAssistantHelper.get_api_endpoint(selected_ai_assistant, region)
assistant_token = None  # Get a new token, or reuse existing if not expired.
assistant_token = AIAssistantHelper.get_api_token(
    assistant_config=selected_ai_assistant, region=region, token=assistant_token
)
```

```python
print("Use the following URL for API requests:")
print(assistant_url)

print("API Interface Type (Auto, OpenAI, or Langchain):")
print(selected_ai_assistant["api_interface"])

print("Bearer Token for API authentication:")
print(assistant_token)
```


---

**Previous**: [Lang Chain LLM Model](../advanced-langchain/lang-chain-llm-model.md) | **Next**: [LLM Evaluation > Meteor](../llm-evaluation/METEOR.md)
