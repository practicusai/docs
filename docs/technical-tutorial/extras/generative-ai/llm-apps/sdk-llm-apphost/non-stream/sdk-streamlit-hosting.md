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

# Hosting of LLM which is built by using SDK


### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
app_name = None  # E.g. 'api-chatbot'
deployment_setting_key = None
app_prefix = None
app_dir = None
```

```python
assert app_name, "Please enter application name"
assert deployment_setting_key, "Please enter deployment_setting_key"
assert app_prefix, "Please enter app_prefix"
assert deployment_setting_key, "Please enter deployment_setting_key"
assert app_prefix, "Please enter app_prefix"
```

```python
import practicuscore as prt

region = prt.get_region()
```

### Test App

```python
# When you finish test, stop this cell. If you dont stop cell always be open.
prt.apps.test_app()
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
my_app_prefixes = region.app_prefix_list
display(my_app_prefixes.to_pandas())
```

```python
my_app_settings = region.app_deployment_setting_list
display(my_app_settings.to_pandas())
```

### Deploying App

```python
prt.apps.deploy(
    deployment_setting_key=deployment_setting_key,  # Deployment Key, ask admin for deployment key
    prefix=app_prefix,  # Apphost deployment extension
    app_name=app_name,
    app_dir=None,  # Directory of files that will be deployed ('None' for current directory)
)
```


## Supplementary Files

### streamlit_app.py
```python
# The below is official Streamlit + Langchain demo.

import streamlit as st
import practicuscore as prt

from langchain_practicus import ChatPracticus

prt.apps.secure_page(
    page_title="🦜🔗 Quickstart App"  # Give page title
)

st.title("🦜🔗 Quickstart App v1")  # Give app title


# This function use our 'api_token' and 'endpoint_url' and return the response.
def generate_response(input_text, endpoint, api):
    model = ChatPracticus(
        endpoint_url=endpoint,  # Give model url
        # Give api token , ask your admin for api
        api_token=api,
        model_id="model",
        verify_ssl=True,
    )

    st.info(model.invoke(input_text).content)  # We are give the input to model and get content


with st.form("my_form"):  # Define our question
    endpoint = st.text_input("Enter your end point url:")
    api = st.text_input("Enter your api token:")
    text = st.text_area(
        "Enter text:",
        "Who is Einstein ?",
    )
    submitted = st.form_submit_button("Submit")  # Define the button

    if submitted:
        generate_response(text, endpoint, api)  # Return the response

```


---

**Previous**: [Build](../../api-llm-apphost/build.md) | **Next**: [Langflow LLM Apphost > Langflow Streamlit Hosting](../../langflow-llm-apphost/langflow-streamlit-hosting.md)
