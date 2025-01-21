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

# Hosting LLM APIs and Apps

```python
import practicuscore as prt
```

```python
# When you finish test, stop this cell. If you dont stop cell always be open.
prt.apps.test_app()
```

After testing our application we can set our configurations and start the deployment process.

```python
import practicuscore as prt
region = prt.get_region()
```

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
app_name = None # E.g. 'api-chatbot'
deployment_setting_key = None
app_prefix = None
app_dir = None
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
my_app_list = region.app_list
display(my_app_list.to_pandas())

print("Using first app name:", app_name)
```

```python
my_app_prefix_list = region.app_prefix_list
display(my_app_prefix_list.to_pandas())

print("Using first app prefix", app_prefix)
```

```python
my_app_settings = region.app_deployment_setting_list
display(my_app_settings.to_pandas())

print("Using first setting with key:", deployment_setting_key)
```

```python
assert app_name, "Please enter application name"
assert deployment_setting_key, "Please enter deployment_setting_key"
assert app_prefix, "Please enter app_prefix"
```

### Deploying app

```python
prt.apps.deploy(
    deployment_setting_key=deployment_setting_key, # Deployment Key, ask admin for deployment key
    prefix=app_prefix, # Apphost deployment extension
    app_name=app_name, 
    app_dir=None # Directory of files that will be deployed ('None' for current directory)
)
```


## Supplementary Files

### streamlit_app.py
```python
# The below is official Streamlit + Langchain demo.

import streamlit as st
import practicuscore as prt
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest
import requests


prt.apps.secure_page(
    page_title="🦜🔗 Quickstart App" # Give page title
)


st.title("🦜🔗 Quickstart App v2") # Give app title


# This function use our 'api_token' and 'endpoint_url' and return the response.
def generate_response(messages, model):

    api_url = "Enter your model api"
    token ="Enter your model token"
    
    practicus_llm_req = PrtLangRequest( # This class need message and model and if u want to stream u should change streaming value false to true
        messages=messages, # Our contest
        lang_model= model, #"gpt-4o", # Select model
        streaming=True, # Streaming mode
        llm_kwargs={"kw1": 123, "kw2": "k2"} # If we have an extra parameters at model.py we can add them here
    )
    
    headers = {
    'authorization': f'Bearer {token}',
    'content-type': 'application/json'
    }
  
    data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True) # Convert our returned parameter to json
    
    with requests.post(api_url, headers=headers, data=data_js, stream=True) as r: 
        for word in r.iter_content(1024):
            yield word.decode("utf-8")

def reset_chat():
    st.session_state["messages"] = []


# Save chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Input chat
user_message = st.chat_input("Write message")
if user_message:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    human_msg = PrtLangMessage(
        content=user_message,
        role = "human"
    )
    
    # Show messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    with st.chat_message("assistant"):
        response = st.write_stream(generate_response([human_msg], "gpt-4o"))
    
    # Show answer
    st.session_state.messages.append({"role": "assistant", "content": response})

# Create a container to hold the button at the bottom
with st.container():
    st.write("")  # Add some empty space to push the button to the bottom
    if st.button("Clear history"):
        reset_chat()
        st.success("History has been cleaned")





```


---

**Previous**: [Sdk Streamlit Hosting](../non-stream/sdk-streamlit-hosting.md) | **Next**: [Langflow LLM Apphost > Langflow Streamlit Hosting](../../langflow-llm-apphost/langflow-streamlit-hosting.md)
