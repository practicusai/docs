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

# LangChain with Streaming

This example demonstrates how to provide human and system messages to a language model and receive a streamed response. The primary steps include:

1. Defining the URL and authentication token.
2. Initializing and interacting with the LLM model.
3. Converting responses into JSON format.
4. Streaming the LLM’s output to your environment.

### Context

The `PrtLangMessage` object stores content and associated roles within a dictionary. This structure serves as your conversation context. To interact with the chat model, you simply create messages—both system-level and user-level—and assign the appropriate role to each.


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.

```python
method = None
model_name = None
model_prefix = None
app_name = None
app_prefix = None
host = None
```

```python
import practicuscore as prt

region = prt.get_region()
```

```python
method = None

# For model APIs
if method == "llm_model":
    model_name = None
    model_prefix = None

# For App APIs
elif method == "llm_app":
    app_name = None
    app_prefix = None

host = None  # e.g. 'company.practicus.io'
```

If you don't know your prefixes and models or apps you can check them out by using the SDK like down below:

```python
my_model_list = region.model_list
display(my_model_list.to_pandas())
```

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
```

```python
my_app_list = prt.apps.get_list()
display(my_app_list.to_pandas())
```

```python
my_app_prefix_list = prt.apps.get_prefix_list()
display(my_app_prefix_list.to_pandas())
```

```python
assert method in ("llm_app", "llm_model"), "Please select a valid method ('llm_app' or 'llm_model')."

if method == "llm_model":
    assert model_name, "Please select an LLM."
    assert model_prefix, "Please select the prefix LLM  deployed."

elif method == "llm_app":
    assert app_name, "Please select an LLM app."
    assert app_prefix, "Please select the prefix LLM app deployed."

assert host, "Please enter your host"
```

Now we can define our API url and it's token.

```python
if method == "llm_model":
    api_url = f"https://{host}/{model_prefix}/{model_name}/"
elif method == "llm_app":
    api_url = f"https://{host}/{app_prefix}/{app_name}/api/"

token = None  # Get a new token, or reuse existing, if not expired
token = prt.models.get_session_token(api_url=api_url, token=token)
```

```python
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse
import requests
```

```python
human_msg = PrtLangMessage(content="Who is einstein? ", role="human")

system_msg = PrtLangMessage(content="Give me answer less than 100 words.", role="system")
```

### Request LLM
- The purpose of PrtLangRequest is to keep the messages, lang_model and streaming mode.
- If you need to data json you can use 'model_dump_json'. This function will return json.

```python
# This class need message and model and if you want to stream,
# you should change streaming value false to true
practicus_llm_req = PrtLangRequest(
    # Our context
    messages=[human_msg, system_msg],
    # Select a model, leave empty for default
    lang_model="",
    # Streaming mode
    streaming=True,
    # If we have a extra parameters at model.py we can add them here
    llm_kwargs={"kw1": 123, "kw2": "k2"},
)

headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}

# Convert our returned parameter to json
data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)
```

```python
with requests.post(api_url, headers=headers, data=data_js, stream=True) as r:
    for response_chunk in r.iter_content(1024):
        print(response_chunk.decode("utf-8"), end="")
```

#### Sample streaming output

Albert Einstein was a theoretical physicist born in 1879 in Germany. He is best known for developing the theory of relativity, particularly the equation \(E=mc^2\), which describes the equivalence of energy (E) and mass (m) with \(c\) being the speed of light. His work revolutionized the understanding of space, time, and gravity. Einstein received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect. He is considered one of the most influential scientists of the 20th century.


---

**Previous**: [LangChain Basics](langchain-basics.md) | **Next**: [Embeddings](embeddings.md)
