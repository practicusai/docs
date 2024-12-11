---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

### Langchain with streaming


In this sample, we aim to give our human and system messages to our model and get a response.
Our main steps:

- Url and token definitions
- Transfer of the llm model
- Json conversion
- Streaming

#### Context
- The purpose of PrtLangMessage is to keep the content and role given into it in a dictionary
- This messages is our context. What u want to ask to chat you need to write this messages and you can give a role.

```python
import practicuscore as prt
region = prt.get_region()
```

```python
my_model_list = region.model_list
display(my_model_list.to_pandas())
model_name = my_model_list[0].name
print("Using first model name:", model_name)
```

```python
my_app_list = region.app_list
display(my_app_list.to_pandas())
app_name = my_app_list[0].name
print("Using first app name:", app_name)
```

```python
my_model_prefixes = region.model_prefix_list
display(my_model_prefixes.to_pandas())
model_prefix = my_model_prefixes[0].key
print("Using first prefix:", model_prefix)
```

```python
my_app_prefix_list = region.app_prefix_list
display(my_app_prefix_list.to_pandas())
app_prefix = my_app_prefix_list[0].prefix
print("Using first app prefix", app_prefix)
```

```python
host = 'company.practicus.io' # Example url -> 'company.practicus.io'
api_url = f"https://{host}/{model_prefix}/{model_name}/"
#api_url = f"https://{host}/{app_prefix}/{app_name}/api/"
token = prt.models.get_session_token(api_url=api_url)
```

```python
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest, PrtLangResponse
import requests
```

```python
human_msg = PrtLangMessage(
    content="Who is einstein? ",
    role = "human"
)

system_msg = PrtLangMessage(
    content="Give me answer less than 100 words.",
    role = "system"
)
```

### Request LLM
- The purpose of PrtLangRequest is to keep the messages, lang_model and streaming mode.
- If you need to data json you can use 'model_dump_json'. This fucniton will return json.

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
    llm_kwargs={"kw1": 123, "kw2": "k2"} 
)

headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'application/json'
}

# Convert our returned parameter to json
data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True) 
```

```python
with requests.post(api_url, headers=headers, data=data_js, stream=True) as r: 
    for response_chunk in r.iter_content(1024): 
        print(response_chunk.decode("utf-8"), end = '')
```

#### Sample streaming output

Albert Einstein was a theoretical physicist born in 1879 in Germany. He is best known for developing the theory of relativity, particularly the equation \(E=mc^2\), which describes the equivalence of energy (E) and mass (m) with \(c\) being the speed of light. His work revolutionized the understanding of space, time, and gravity. Einstein received the Nobel Prize in Physics in 1921 for his explanation of the photoelectric effect. He is considered one of the most influential scientists of the 20th century.

```python

```


---

**Previous**: [Build](../app-building/build.md) | **Next**: [Langchain Basics](langchain-basics.md)
