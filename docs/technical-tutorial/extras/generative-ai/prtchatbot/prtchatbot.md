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
app_name = 'prtchatbot3' # E.g. 'api-chatbot'
deployment_setting_key = 'appdepl'
app_prefix = 'apps'
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

```python

```


## Supplementary Files

### Home.py
```python
import streamlit as st
import uuid
import random
from chatbot import get_response_from_model
from db import save_message_to_db, get_session_messages, delete_session_from_db, create_connection
import datetime

st.set_page_config(page_title="Chatbot App", layout="wide")
st.title("🤖 Practicus Proxy Chatbot")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "selectbox_key" not in st.session_state:
    st.session_state.selectbox_key = str(random.randint(0, 1_000_000))

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("main_form"):
    st.text_input("💡 Session Title", value=f"Session - {st.session_state.session_id[:8]}", key="session_title")

    st.markdown("### Actions:")
    action_cols = st.columns([1, 1, 1, 1])

    if action_cols[0].form_submit_button("🆕 New Session"):
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.selected_session_id = None
        st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
        st.rerun()

    if action_cols[1].form_submit_button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        if st.session_state.selected_session_id:
            delete_session_from_db(st.session_state.selected_session_id)
        st.rerun()

    if action_cols[2].form_submit_button("💾 Save Session"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        title = st.session_state.session_title
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = %s", (st.session_state.session_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO sessions (session_id, user_id, title, created_at, language) VALUES (%s, %s, %s, %s, %s)",
                           (st.session_state.session_id, 1, title, now, "English"))
        else:
            cursor.execute("UPDATE sessions SET title = %s, language = %s WHERE session_id = %s",
                           (title, "English", st.session_state.session_id))
        connection.commit()
        cursor.close()
        connection.close()
        st.success("✅ Session saved!")

    if action_cols[3].form_submit_button("🗑️ Delete Session"):
        if st.session_state.selected_session_id:
            delete_session_from_db(st.session_state.selected_session_id)
            st.session_state.chat_history = []
            st.session_state.selected_session_id = None
            st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
            st.rerun()

model_name_list = ["llm-proxy", "llama-3-70b"]
selected_model_name = st.selectbox("Select Model", model_name_list)

connection = create_connection()
cursor = connection.cursor()
cursor.execute("SELECT session_id, title, created_at FROM sessions ORDER BY created_at DESC")
saved_sessions = cursor.fetchall()
session_labels = ["New Session"] + [f"{row[1]} ({row[2]})" for row in saved_sessions]
session_ids = [None] + [row[0] for row in saved_sessions]
cursor.close()
connection.close()

if "selected_session_id" not in st.session_state:
    st.session_state.selected_session_id = None

default_index = 0 if st.session_state.selected_session_id is None else session_ids.index(st.session_state.selected_session_id)

selected_index = st.selectbox(
    "💬 Load Session", 
    options=range(len(session_labels)), 
    format_func=lambda i: session_labels[i],
    index=default_index,
    key=st.session_state.selectbox_key
)

selected_session = session_ids[selected_index]
st.session_state.selected_session_id = selected_session

if selected_session:
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT content, role FROM messages WHERE session_id = %s ORDER BY created_at", (selected_session,))
    messages = cursor.fetchall()
    st.session_state.chat_history = [{"role": role, "content": content} for content, role in messages]
    cursor.close()
    connection.close()
    st.session_state.session_id = selected_session
    st.success(f"🔄 Session loaded.")

if "chat_history" in st.session_state:
    for chat in st.session_state.chat_history:
        st.chat_message(chat["role"]).write(chat["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.chat_message("user").write(user_input)
    response = get_response_from_model(selected_model_name, user_input)
    st.chat_message("assistant").write(response)

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    save_message_to_db(st.session_state.session_id, "user", user_input)
    save_message_to_db(st.session_state.session_id, "assistant", response)
```

### chatbot.py
```python
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


```

### db.py
```python
import psycopg2
import datetime

def create_connection():
    try:
        connection = psycopg2.connect(
            host="test-db-1.c34rytcb0n56.us-east-1.rds.amazonaws.com",
            database="llm",
            user="prt_analytics_user",
            password="prt_analytics_pwd"
        )
        return connection
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def save_message_to_db(session_id, role, content):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = %s", (session_id,))
        result = cursor.fetchone()

        if result is None:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO sessions (session_id, title, created_at, language) VALUES (%s, %s, %s, %s)",
                           (session_id, f"Oturum - {session_id[:8]}", now, "English"))
            connection.commit()

        cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)", 
                       (session_id, role, content))
        connection.commit()
        cursor.close()
        connection.close()

def get_session_messages(session_id):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT content, role FROM messages WHERE session_id = %s ORDER BY created_at", (session_id,))
    messages = cursor.fetchall()
    cursor.close()
    connection.close()
    return [{"role": role, "content": content} for content, role in messages]

def delete_session_from_db(session_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
        connection.commit()
        cursor.close()
        connection.close()

```


---

**Previous**: [Using Databases](../databases/using-databases.md) | **Next**: [Advanced LangChain > Lang Chain LLM Model](../advanced-langchain/lang-chain-llm-model.md)
