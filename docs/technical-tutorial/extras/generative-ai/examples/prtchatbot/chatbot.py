import requests
import time
from db import save_message_to_db, get_session_messages
import streamlit as st
from practicuscore.gen_ai import ChatCompletionRequest
import practicuscore as prt
import jwt
from datetime import datetime, timedelta
from typing import Optional


def get_jwt_expiry(token: str) -> Optional[datetime]:
    """
    Extracts the expiry date from a JWT token without verifying its signature.

    Args:
        token (str): The JWT token string.

    Returns:
        Optional[datetime]: The expiry date as a datetime object if available, otherwise None.
    """
    decoded_payload: dict = jwt.decode(token, options={"verify_signature": False})
    expiry_timestamp: Optional[int] = decoded_payload.get("exp")

    if expiry_timestamp is None:
        return None

    return datetime.utcfromtimestamp(expiry_timestamp)

def get_response_from_model(model_name, user_input):
    return call_practicus_model(user_input, model_name)

def get_token_for_model(model_name):
    token_data = st.session_state.get(f"token_{model_name}", None)


    if not token_data or token_data["expires_at"] < time.time():
        api_url = f"https://dev.practicus.io/models/{model_name}/"
        token = prt.models.get_session_token(api_url=api_url)

        expires_at = time.time() + 3 * 60 * 60
        st.session_state[f"token_{model_name}"] = {"token": token, "expires_at": expires_at}


        return token
    else:
        return token_data["token"]


def call_practicus_model(user_input, model_name):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    token = get_token_for_model(model_name)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *st.session_state.chat_history,
        {"role": "user", "content": user_input},
    ]

    chat_request = ChatCompletionRequest(model=model_name, messages=messages, temperature=0.7, max_tokens=512)

    payload = chat_request.model_dump()
    response = requests.post(f"https://dev.practicus.io/models/{model_name}/", headers=headers, json=payload)

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
