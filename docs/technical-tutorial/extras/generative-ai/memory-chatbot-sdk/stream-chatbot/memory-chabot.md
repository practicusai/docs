---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

# Memory Chatbot

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
app_name = "..."  # E.g. 'api-chatbot'
deployment_setting_key = "..."
app_prefix = "..."
app_dir = None
```

##### If you don't know your prefixes and deployments you can check them out by using the SDK like down below:
 

```python
my_app_list = prt.apps.get_list()
display(my_app_list.to_pandas())

print("Using first app name:", app_name)
```

```python
my_app_prefix_list = prt.apps.get_prefix_list()
display(my_app_prefix_list.to_pandas())

print("Using first app prefix", app_prefix)
```

```python
my_app_settings = prt.apps.get_deployment_setting_list()
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
    deployment_setting_key=deployment_setting_key,  # Deployment Key, ask admin for deployment key
    prefix=app_prefix,  # Apphost deployment extension
    app_name=app_name,
    app_dir=None,  # Directory of files that will be deployed ('None' for current directory)
)
```

```python

```


## Supplementary Files

### streamlit_app.py
```python
import streamlit as st
import psycopg2
import practicuscore as prt
from practicuscore.gen_ai import PrtLangMessage, PrtLangRequest
import requests
import html
import datetime

db_config = {"host": "...", "database": "...", "user": "...", "password": "..."}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_message TEXT,
    bot_response TEXT,
    session_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


def save_conversation(user_message, bot_response, session_id):
    if user_message and bot_response:
        cursor.execute(
            "INSERT INTO conversations (user_message, bot_response, session_id) VALUES (%s, %s, %s)",
            (user_message, bot_response, session_id),
        )
        conn.commit()
    elif user_message:
        cursor.execute(
            "INSERT INTO conversations (user_message, session_id) VALUES (%s, %s)", (user_message, session_id)
        )
        conn.commit()


def get_conversation(session_id=None, limit=5):
    if session_id:
        cursor.execute(
            """
            SELECT user_message, bot_response 
            FROM conversations 
            WHERE session_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """,
            (session_id, limit),
        )
    else:
        cursor.execute(
            """
            SELECT user_message, bot_response 
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT %s
        """,
            (limit,),
        )
    return cursor.fetchall()


def get_conversation_with_timestamps(session_id=None):
    if session_id:
        cursor.execute(
            "SELECT user_message, bot_response, timestamp FROM conversations WHERE session_id = %s ORDER BY timestamp DESC",
            (session_id,),
        )
    else:
        cursor.execute("SELECT user_message, bot_response, timestamp FROM conversations ORDER BY timestamp DESC")
    return cursor.fetchall()


def get_all_session_ids():
    cursor.execute("""
        SELECT session_id
        FROM conversations
        GROUP BY session_id
        ORDER BY MAX(timestamp) DESC
    """)
    return [row[0] for row in cursor.fetchall()]


def summarize_conversation(conversation_history):
    summary = "This is a summary of the conversation:\n"
    for user_message, bot_response in conversation_history:
        summary += f"User: {user_message}\nBot: {bot_response}\n"
    return summary


def render_chat_history(conversation_history):
    if conversation_history:
        for user_message, bot_response, timestamp in reversed(conversation_history):
            user_message = user_message if user_message is not None else ""
            bot_response = bot_response if bot_response is not None else ""
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown"

            st.markdown(
                f"""
                <div style='display: flex; align-items: flex-start; margin-bottom: 10px;'>
                    <div style='font-size: 1.5em; margin-right: 10px;'>👤</div>
                    <div style='background-color: #f0f8ff; color: #000; padding: 10px; border-radius: 10px; max-width: 70%;'>
                        {html.escape(user_message)}
                        <div style='font-size: 0.8em; color: #888; text-align: right;'>{formatted_timestamp}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style='display: flex; align-items: flex-start; flex-direction: row-reverse; margin-bottom: 10px;'>
                    <div style='font-size: 1.5em; margin-left: 10px;'>🤖</div>
                    <div style='background-color: #e8f5e9; color: #000; padding: 10px; border-radius: 10px; max-width: 70%;'>
                        {html.escape(bot_response)}
                        <div style='font-size: 0.8em; color: #888; text-align: right;'>{formatted_timestamp}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown("No conversation history found.")


def delete_session(session_id):
    cursor.execute("DELETE FROM conversations WHERE session_id = %s", (session_id,))
    conn.commit()


def generate_response(prompt, model, session_id=None):
    api_url = "..."
    token = prt.models.get_session_token(api_url=api_url)

    conversation_history = get_conversation(session_id=session_id)
    context = summarize_conversation(conversation_history)

    full_prompt = context + "User: " + prompt

    practicus_llm_req = PrtLangRequest(
        messages=[PrtLangMessage(content=full_prompt, role="human")], lang_model=model, streaming=True
    )

    headers = {"authorization": f"Bearer {token}", "content-type": "application/json"}

    data_js = practicus_llm_req.model_dump_json(indent=2, exclude_unset=True)

    with requests.post(api_url, headers=headers, data=data_js, stream=True) as r:
        for word in r.iter_content(1024):
            yield word.decode("utf-8")


st.set_page_config(page_title="Chatbot", layout="wide")
st.title("Chatbot App")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "session_saved" not in st.session_state:
    st.session_state["session_saved"] = False

if "selected_session_id" not in st.session_state:
    st.session_state["selected_session_id"] = None

chat_placeholder = st.empty()
with chat_placeholder.container():
    if st.session_state["selected_session_id"]:
        conversation_history = get_conversation_with_timestamps(session_id=st.session_state["selected_session_id"])
        render_chat_history(conversation_history)
    else:
        st.write("Your conversation history will appear here.")

if st.button("Refresh"):
    if st.session_state["selected_session_id"]:
        conversation_history = get_conversation_with_timestamps(session_id=st.session_state["selected_session_id"])
        with chat_placeholder.container():
            render_chat_history(conversation_history)

input_placeholder = st.empty()
with input_placeholder.container():
    user_message = st.text_input("Your messages:", placeholder="Write here...", key="chat_input")
    if st.button("Send"):
        if not st.session_state["selected_session_id"]:
            st.session_state["selected_session_id"] = "temporary_session"

        st.session_state["messages"].append({"role": "user", "content": user_message})
        bot_response = ""
        for chunk in generate_response(user_message, "gpt-4o", session_id=st.session_state["selected_session_id"]):
            bot_response += chunk
            st.session_state["messages"].append({"role": "bot", "content": chunk})
            with chat_placeholder.container():
                updated_conversation = get_conversation_with_timestamps(
                    session_id=st.session_state["selected_session_id"]
                ) + [(user_message, bot_response, datetime.datetime.now())]
                render_chat_history(updated_conversation)

        if bot_response.strip():
            save_conversation(user_message, bot_response, st.session_state["selected_session_id"])
            conversation_history = get_conversation_with_timestamps(session_id=st.session_state["selected_session_id"])
            with chat_placeholder.container():
                render_chat_history(conversation_history)
        else:
            st.warning("A blank response was received, not recorded.")

with st.sidebar:
    st.header("Chat Management")

    st.subheader("Registered Chats")
    all_session_ids = get_all_session_ids()
    if all_session_ids:
        for sid in all_session_ids:
            cols = st.columns([9, 1])
            with cols[0]:
                if st.button(f"Session: {sid}"):
                    st.session_state["selected_session_id"] = sid
                    st.session_state["session_saved"] = True
            with cols[1]:
                if st.button("❌", key=f"delete_{sid}"):
                    delete_session(sid)
                    st.session_state["selected_session_id"] = None
    else:
        st.write("No registered chat found.")

    st.subheader("Start New Chat")
    if st.button("New Chat"):
        st.session_state["selected_session_id"] = None
        st.session_state["messages"] = []
        st.session_state["session_saved"] = False
        st.query_params = {}

    if st.session_state["session_saved"]:
        st.write(f"Selected Session ID: {st.session_state['selected_session_id']}")

    if st.button("Save"):
        if not st.session_state["session_saved"]:
            st.session_state["selected_session_id"] = st.text_input("New Chat ID", placeholder="Enter new chat id")
        else:
            cursor.execute(
                "SELECT session_id FROM conversations WHERE session_id = %s", (st.session_state["selected_session_id"],)
            )
            if cursor.fetchone():
                st.warning("This session is already exist.")
            else:
                cursor.execute(
                    "INSERT INTO conversations (session_id) VALUES (%s)", (st.session_state["selected_session_id"],)
                )
                conn.commit()
                st.success(f"Chat saved: {st.session_state['selected_session_id']}")
                st.session_state["session_saved"] = True

```


---

**Previous**: [Chatbot-Console-OpenAI](../chatbot-console-openai.md) | **Next**: [Data Analysis > Plot > Introduction](../../../data-analysis/plot/introduction.md)
