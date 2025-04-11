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
