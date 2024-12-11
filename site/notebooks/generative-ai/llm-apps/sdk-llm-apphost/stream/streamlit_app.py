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
        llm_kwargs={"kw1": 123, "kw2": "k2"} # If we have a extra parameters at model.py we can add them here 
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




