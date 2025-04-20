import streamlit as st
import uuid
import random
from chatbot import get_response_from_model
from db import save_message_to_db, get_session_messages, delete_session_from_db, create_connection, update_message_in_db
import datetime
import textwrap

st.set_page_config(page_title="Chatbot App", layout="wide")
st.title("🤖 Practicus Proxy Chatbot")

if "live_summary" not in st.session_state:
    st.session_state.live_summary = "No summary generated yet."

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    model_name_list = ["llm-proxy", "llama-3-70b", "tinyllama1b"]
    selected_model_name = st.selectbox("📦 Select Model", model_name_list)

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "selectbox_key" not in st.session_state:
        st.session_state.selectbox_key = str(random.randint(0, 1_000_000))

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

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

    if st.session_state.selected_session_id in session_ids:
        default_index = session_ids.index(st.session_state.selected_session_id)
    else:
        default_index = 0

    selected_index = st.selectbox(
        "💬 Select Session",
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
        st.success("🔄 Session loaded.")

    st.text_input("💡 Session Title", value=f"Session - {st.session_state.session_id[:8]}", key="session_title")

    if st.button("🆕 New Session"):
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.selected_session_id = None
        st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
        st.session_state.live_summary = "No summary generated yet."
        st.rerun()

    if st.button("💾 Save Session"):
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

    if st.button("🗑️ Delete Session"):
        if st.session_state.selected_session_id:
            delete_session_from_db(st.session_state.selected_session_id)
            st.session_state.chat_history = []
            st.session_state.selected_session_id = None
            st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
            st.session_state.live_summary = "No summary generated yet."
            st.rerun()

    with st.expander("🧠 Live Conversation Summary", expanded=True):
        st.markdown(st.session_state.live_summary)


if "chat_history" in st.session_state:
    for chat in st.session_state.chat_history:
        st.chat_message(chat["role"]).write(chat["content"])

    with st.expander("🧠 Edit/Delete Past User Messages"):
        for i, chat in enumerate(st.session_state.chat_history):
            if chat["role"] != "user":
                continue

            col1, col2, col3, col4 = st.columns([6, 1, 1, 1])

            with col1:
                new_content = st.text_area(f"Message {i+1}", value=chat["content"], key=f"context_edit_{i}")

            with col2:
                if st.button("❌", key=f"delete_context_{i}"):
                    connection = create_connection()
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM messages WHERE session_id = %s AND content = %s AND role = 'user'",
                                   (st.session_state.session_id, chat["content"]))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    st.session_state.chat_history.pop(i)
                    st.rerun()

            with col3:
                if st.button("🔼 Take Before", key=f"fork_before_{i}"):
                    new_history = st.session_state.chat_history[:i+1]
                    context_text = "\n".join([f"{m['role']}: {m['content']}" for m in new_history])
                    summary_prompt = textwrap.dedent(f"""
                        Here is a part of a previous conversation. 
                        Please summarize it briefly and meaningfully.
                        This summary will be used as context for a new conversation.

                        Conversation:
                        {context_text}
                    """).strip()
                    summary_response = get_response_from_model(selected_model_name, summary_prompt)
                    intro_msg = f"""
Context summary transferred from the previous conversation:
{summary_response}

This chat will continue based on the summarized context above.
What is your first question?
                    """.strip()
                    new_history.append({"role": "assistant", "content": intro_msg})
                    st.session_state.chat_history = new_history
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.selected_session_id = None
                    st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
                    st.session_state.live_summary = summary_response
                    st.rerun()

            with col4:
                if st.button("🔽 Take After", key=f"fork_after_{i}"):
                    new_history = st.session_state.chat_history[i:]
                    context_text = "\n".join([f"{m['role']}: {m['content']}" for m in new_history])
                    summary_prompt = textwrap.dedent(f"""
                        Here is a part of a previous conversation. 
                        Please summarize it briefly and meaningfully.
                        This summary will be used as context for a new conversation.

                        Conversation:
                        {context_text}
                    """).strip()
                    summary_response = get_response_from_model(selected_model_name, summary_prompt)
                    intro_msg = f"""
Context summary transferred from the previous conversation:
{summary_response}

This chat will continue based on the summarized context above.
What is your first question?
                    """.strip()
                    new_history.append({"role": "assistant", "content": intro_msg})
                    st.session_state.chat_history = new_history
                    st.session_state.session_id = str(uuid.uuid4())
                    st.session_state.selected_session_id = None
                    st.session_state.selectbox_key = str(random.randint(0, 1_000_000))
                    st.session_state.live_summary = summary_response
                    st.rerun()

            if new_content != chat["content"]:
                update_message_in_db(st.session_state.session_id, chat["content"], new_content)
                st.session_state.chat_history[i]["content"] = new_content

with st.container():
    st.markdown("---")
    if st.button("📝 Chat Summary") and st.session_state.chat_history:
        recent = st.session_state.chat_history[-4:]
        recent_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        current_summary = st.session_state.live_summary or "No summary yet."
        summary_prompt = textwrap.dedent(f"""
            Below is the previous conversation summary.

            Please update the summary since new messages were added.

            --- Previous Summary ---
            {current_summary}

            --- New Messages ---
            {recent_text}
        """).strip()
        summary_response = get_response_from_model(selected_model_name, summary_prompt)
        st.markdown("### 📋 Updated Chat Summary")
        st.info(summary_response)

user_input = st.chat_input("Type your message...")

if user_input:
    st.chat_message("user").write(user_input)
    response = get_response_from_model(selected_model_name, user_input)
    st.chat_message("assistant").write(response)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    save_message_to_db(st.session_state.session_id, "user", user_input)
    save_message_to_db(st.session_state.session_id, "assistant", response)
    recent_text = f"user: {user_input}\nassistant: {response}"
    live_summary_prompt = textwrap.dedent(f"""
        Below is the current summary of the conversation.

        Please update it using the new exchange.

        --- Previous Summary ---
        {st.session_state.live_summary}

        --- New Messages ---
        {recent_text}
    """).strip()
    st.session_state.live_summary = get_response_from_model(selected_model_name, live_summary_prompt)

