import requests
from db import save_message_to_db, get_session_messages
import streamlit as st
from practicuscore.gen_ai import ChatCompletionRequest
import practicuscore as prt


def get_response_from_model(model_name, user_input):
    return call_practicus_model(user_input, model_name)


def call_practicus_model(user_input, model_name):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    api_url = f"https://dev.practicus.io/models/{model_name}/"
    token = prt.models.get_session_token(api_url=api_url)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *st.session_state.chat_history,
        {"role": "user", "content": user_input},
    ]

    chat_request = ChatCompletionRequest(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=512  

    )

    payload = chat_request.model_dump()
    response = requests.post(api_url, headers=headers, json=payload)

    try:
        data = response.json()
    except Exception as e:
        return f"❌ Failed to parse response: {e}"

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    elif "content" in data:
        return data["content"]
    else:
        return f"⚠️ Unexpected response: {data}"

