---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Flow hosting of Langflow by using Streamlit


### Defining parameters from region.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
app_name = None # E.g. 'api-chatbot'
deployment_setting_key = None
app_prefix = None
app_dir = None

```

```python
assert app_name, "Please enter application name"
assert deployment_setting_key, "Please enter deployment_setting_key"
assert app_prefix, "Please enter app_prefix"
```

```python
import practicuscore as prt
region = prt.get_region()
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
my_app_prefix_list = region.app_prefix_list
display(my_app_prefix_list.to_pandas())
app_prefix = my_app_prefix_list[0].prefix
print("Using first app prefix", app_prefix)
```

```python
my_app_list = region.app_list
display(my_app_list.to_pandas())
app_name = my_app_list[0].name
print("Using first app name:", app_name)
```

```python
my_app_settings = region.app_deployment_setting_list
display(my_app_settings.to_pandas())
deployment_setting_key = my_app_settings[1].key
print("Using first setting with key:", deployment_setting_key)
```

## Testing App


First of all we need to create a "Basic Prompting (Hello, World)" flow at langflow and export the json of it.


After exporting the json and save it within current directory of this tutorial, you should test it if it's working.

```python
from langflow.load import run_flow_from_json

result = run_flow_from_json(
    flow="Flow.json",
    input_value="What is the capital of Australia?"
)

run_output = result[0]
result_data = run_output.outputs[0]
message_obj = result_data.results['message']
message_text = message_obj.data['text']

message_text
```

Now we can create our own stream-lit app and use json of our flow within stream-lit's front-end. You can check-out our streamlit_app.py:

[View streamlit_app.py](streamlit_app.py)


After creating/editing stream_app.py we could test it by hosting it as test by using our SDK:

```python
# When you finish test, stop this cell. If you dont stop cell always be open.
prt.apps.test_app()
```

### Deploying App

```python
import practicuscore as prt

prt.apps.deploy(
    deployment_setting_key=deployment_setting_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None # Current dir
)
```

After the deployment process completed we could enter UI url (e.g. https://dev.practicus.io/apps/langflow-json-test/v1/) to show-case our app.


## Supplementary Files

### streamlit_app.py
```python
import practicuscore as prt
import streamlit as st
from langflow.load import run_flow_from_json

# The below will secure the page by authenticating and authorizing users with Single-Sign-On.
# Please note that security code is only activate when the app is deployed.
# Pages are always secure, even without the below, during development and only the owner can access them.
prt.apps.secure_page(
    page_title="Hello World App",
    must_be_admin=False,
)


def main():
    # The below is standard Streamlit code..
    st.title("My App on Practicus AI")

    st.markdown("##### Welcome to the front-end of your flow")

    # Initialize session state to store chat messages if not already initialized.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display all messages stored in session state in the chat interface.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # When the user inputs a message, add it to the chat history and display it.
    if prompt := st.chat_input("I'm your flow, how may I help you?"):
        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        # Display user message in chat message container
        with st.chat_message(
                "user"
        ):
            st.write(prompt)
        # Display assistant response in chat message container
        with st.chat_message(
                "assistant"
        ):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt)
                message_placeholder.write(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )


def run_flow(message, flow_json):
    result = run_flow_from_json(flow=flow_json,
                                input_value=message,
                                fallback_to_env_vars=True)  # False by default
    return result


# Function to generate a response from the flow based on the user's input.
def generate_response(prompt):
    # Log the user's question.
    # logging.info(f"question: {prompt}")

    # Run the flow to get the response.
    response = run_flow(message=prompt, flow_json='Flow.json')

    run_output = response[0]
    result_data = run_output.outputs[0]
    message_obj = result_data.results['message']
    message_text = message_obj.data['text']

    try:
        # Log and return the assistant's response.
        #logging.info(f"answer: {message_obj}")
        return message_text
    except Exception as exc:
        # Log any errors and return a fallback message.
        #logging.error(f"error: {exc}")
        return "Sorry, there was a problem finding an answer for you."


# Run the main function to start the Streamlit app.
if __name__ == "__main__":
    main()

```


---

**Previous**: [Sdk Streamlit Hosting](../sdk-llm-apphost/non-stream/sdk-streamlit-hosting.md) | **Next**: [Milvus Embedding And LangChain > Milvus Chain](../../milvus-embedding-and-langchain/milvus-chain.md)
