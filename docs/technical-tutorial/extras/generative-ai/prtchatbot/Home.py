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
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id, title, created_at, language) VALUES (%s, %s, %s, %s, %s)",
                (st.session_state.session_id, 1, title, now, "English"),
            )
        else:
            cursor.execute(
                "UPDATE sessions SET title = %s, language = %s WHERE session_id = %s",
                (title, "English", st.session_state.session_id),
            )
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

default_index = (
    0 if st.session_state.selected_session_id is None else session_ids.index(st.session_state.selected_session_id)
)

selected_index = st.selectbox(
    "💬 Load Session",
    options=range(len(session_labels)),
    format_func=lambda i: session_labels[i],
    index=default_index,
    key=st.session_state.selectbox_key,
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
