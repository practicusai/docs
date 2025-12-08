---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

```python
import openai
import psycopg2
from datetime import datetime
```

### **Code Functionality**
This code attempts to establish a connection to a PostgreSQL database using the `psycopg2` library. If the connection is successful, it outputs a success message; otherwise, it captures and displays the error.

---

### **Key Components**

1. **`try` Block**:
   - Attempts to connect to the database using the `psycopg2.connect()` function.
   - Parameters such as `host`, `database`, `user`, and `password` are provided to define the connection details.

2. **`except Exception as e`**:
   - Captures any exceptions (errors) that occur during the connection attempt.
   - Prints an error message that includes details of the exception (`e`).

3. **Success Message**:
   - If the connection is successful, `"Connection successful!"` is printed.


```python
try:
    connection = psycopg2.connect(host="...", database="...", user="...", password="...")
    print("Connection successful!")
except Exception as e:
    print(f"Connection error: {e}")
```

# Configuration Setup for OpenAI API and Database

### **Code Functionality**
This code sets up the necessary configurations for:
1. Accessing the OpenAI API by specifying the API key.
2. Defining database connection parameters in a dictionary for later use.

---

### **Key Components**

1. **`openai.api_key = "..."`**
   - Sets the API key for authenticating with the OpenAI API.
   - The key is a string that identifies the user and grants access to OpenAI's services.
   - **Purpose**: Enable interaction with OpenAI's models (e.g., GPT) in the application.

2. **`db_config`**
   - A dictionary containing database connection parameters:
     - **`host`**: The database server address (e.g., IP or domain name).
     - **`database`**: The name of the specific database to connect to.
     - **`user`**: The username for authentication.
     - **`password`**: The password for the database user.
   - **Purpose**: Provide reusable configuration details for connecting to the PostgreSQL database.


```python
openai.api_key = "..."

db_config = {"host": "...", "database": "...", "user": "...", "password": "..."}
```

# Creating a Conversations Table in PostgreSQL

### **Code Functionality**
This code connects to a PostgreSQL database, creates a cursor object to execute SQL commands, and ensures that a `conversations` table exists. If the table doesn't exist, it is created. Finally, the changes are committed to the database.

---

### **Key Components**

1. **Database Connection**:
   - **`conn = psycopg2.connect(**db_config)`**:
     - Establishes a connection to the database using the `db_config` dictionary defined earlier.
   - **`cursor = conn.cursor()`**:
     - Creates a cursor object, which is used to execute SQL commands.

2. **SQL Command to Create Table**:
   - **`CREATE TABLE IF NOT EXISTS conversations`**:
     - Creates a table named `conversations` if it does not already exist.
   - **Table Schema**:
     - **`id SERIAL PRIMARY KEY`**: Auto-incrementing unique identifier for each record.
     - **`session_id TEXT NOT NULL`**: A session identifier for grouping related conversations.
     - **`user_message TEXT`**: Stores messages sent by the user.
     - **`bot_response TEXT`**: Stores the chatbot's responses.
     - **`user_id TEXT`**: Identifies the user, allowing for user-specific data tracking.
     - **`timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP`**: Records the time of each interaction, with a default value of the current time.

3. **Commit Changes**:
   - **`conn.commit()`**:
     - Saves the executed SQL changes (table creation) to the database.


```python
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()
```

```python
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_message TEXT,
    bot_response TEXT,
    user_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
```

# Saving Conversations to the Database

### **Code Functionality**
This function, `save_conversation`, inserts a single conversation record into the `conversations` table in the PostgreSQL database. It logs both the user message and the bot response, along with identifying information like the user ID and session ID.

---

### **Key Components**

1. **Function Parameters**:
   - **`user_message`**: The message sent by the user.
   - **`bot_response`**: The chatbot's reply to the user.
   - **`user_id`**: A unique identifier for the user, enabling user-specific conversation tracking.
   - **`session_id`**: A unique identifier for the session, grouping related conversations.

2. **SQL Command**:
   - **`INSERT INTO conversations (...) VALUES (%s, %s, %s, %s)`**:
     - Adds a new record to the `conversations` table with the provided values.
     - Placeholders (`%s`) are used to securely pass dynamic data into the query, preventing SQL injection.

3. **Committing Changes**:
   - **`conn.commit()`**:
     - Saves the new conversation record to the database.


```python
def save_conversation(user_message, bot_response, user_id, session_id):
    cursor.execute(
        "INSERT INTO conversations (user_message, bot_response, user_id, session_id) VALUES (%s, %s, %s, %s)",
        (user_message, bot_response, user_id, session_id),
    )
    conn.commit()
```

# Retrieving Conversations from the Database

### **Code Functionality**
The `get_conversation` function retrieves conversation records from the `conversations` table in the PostgreSQL database. It allows filtering by user ID, session ID, or both, and returns the conversation messages in chronological order.

---

### **Key Components**

1. **Function Parameters**:
   - **`user_id`** (optional): Filters the records by a specific user.
   - **`session_id`** (optional): Filters the records by a specific session.
   - If no parameters are provided, it retrieves all conversations.

2. **Conditional Logic**:
   - **Both `user_id` and `session_id` provided**:
     - Retrieves conversations matching both user and session.
   - **Only `user_id` provided**:
     - Retrieves all conversations for the specified user.
   - **Only `session_id` provided**:
     - Retrieves all conversations for the specified session.
   - **No parameters**:
     - Retrieves all conversations in the table.

3. **SQL Query**:
   - **Dynamic Filtering**:
     - Uses placeholders (`%s`) to securely include parameters in the query, preventing SQL injection.
   - **Ordering**:
     - Results are sorted by the `timestamp` column in ascending order to maintain chronological order.

4. **Returning Data**:
   - **`cursor.fetchall()`**:
     - Fetches all matching rows from the query result, returning a list of tuples with `user_message` and `bot_response`.


```python
def get_conversation(user_id=None, session_id=None):
    if user_id and session_id:
        cursor.execute(
            "SELECT user_message, bot_response FROM conversations WHERE user_id = %s AND session_id = %s ORDER BY timestamp ASC",
            (user_id, session_id),
        )
    elif user_id:
        cursor.execute(
            "SELECT user_message, bot_response FROM conversations WHERE user_id = %s ORDER BY timestamp ASC", (user_id,)
        )
    elif session_id:
        cursor.execute(
            "SELECT user_message, bot_response FROM conversations WHERE session_id = %s ORDER BY timestamp ASC",
            (session_id,),
        )
    else:
        cursor.execute("SELECT user_message, bot_response FROM conversations ORDER BY timestamp ASC")
    return cursor.fetchall()
```

# Chatting with OpenAI's API

### **Code Functionality**
The `chat_with_openai` function interacts with OpenAI's GPT model to generate a response based on a user's input prompt. It handles potential errors gracefully and returns either the AI's response or an error message.

---

### **Key Components**

1. **Input Parameter**:
   - **`prompt`**: A string input provided by the user, serving as the basis for the AI's response.

2. **OpenAI API Call**:
   - **`openai.ChatCompletion.create()`**:
     - Sends a request to OpenAI's API to generate a response.
     - **Parameters**:
       - **`model="gpt-3.5-turbo"`**: Specifies the model to be used.
       - **`messages`**: A list containing the conversation context, where the user's input is structured as a message with the role "user."

3. **Response Handling**:
   - **`response['choices'][0]['message']['content']`**:
     - Extracts the AI's generated text from the API response.

4. **Error Handling**:
   - **`try` and `except`**:
     - Catches any exceptions during the API call (e.g., network issues, API errors).
     - Returns an error message if an exception occurs.


```python
def chat_with_openai(prompt):
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Hata: {e}"
```

# Main Function for Chatbot Interaction

### **Code Functionality**
The `main` function serves as the entry point for a chatbot application. It facilitates interaction between the user and the chatbot by handling user inputs, fetching previous conversation history, generating responses via OpenAI's API, and saving the new interactions to a database.

---

### **Key Components**

1. **Welcome Message**:
   - **`print("Welcome to Chatbot! (Type 'exit' to exit)")`**:
     - Greets the user and provides instructions to exit the chatbot.

2. **User and Session Information**:
   - **`user_id`**:
     - Captures the user's unique identifier.
   - **`session_id`**:
     - Captures the session identifier, where a new value signifies a new chat session.

3. **Fetching Conversation History**:
   - **`get_conversation(user_id, session_id)`**:
     - Retrieves previous conversations for the provided `user_id` and `session_id`.
   - Displays the history to the user, if available, for context.

4. **Chat Loop**:
   - **`while True`**:
     - Keeps the chatbot active until the user types "exit".
   - **User Input**:
     - Prompts the user to enter a message.
     - Exits the loop if the input is "exit".
   - **Generating Bot Response**:
     - **`chat_with_openai(user_message)`**:
       - Sends the user's message to OpenAI's API and fetches a bot response.
   - **Displaying Conversation**:
     - Prints both the user's message and the bot's response to the console.
   - **Saving the Conversation**:
     - **`save_conversation(user_message, bot_response, user_id, session_id)`**:
       - Stores the interaction in the database for future reference.


```python
def main():
    print("Welcome to Chatbot! (Type 'exit' to exit)")
    user_id = input("Please enter your user ID: ")
    session_id = input("Please enter your session ID (enter a new value for the new session): ")

    conversation_history = get_conversation(user_id=user_id, session_id=session_id)
    if conversation_history:
        print("\nPrevious Conversation History:")
        for user_message, bot_response in conversation_history:
            print(f"User: {user_message}\nBot: {bot_response}\n")

    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            print("Exit is in progress...")
            break

        bot_response = chat_with_openai(user_message)
        print(f"User: {user_message}")
        print(f"Bot: {bot_response}")

        save_conversation(user_message, bot_response, user_id, session_id)
```

# Running the Chatbot Application

### **Code Functionality**
This block ensures the proper execution of the chatbot application by calling the `main` function and safely closing database resources when the program ends.

---

### **Key Components**

1. **Entry Point**:
   - **`if __name__ == "__main__":`**:
     - Ensures that the `main()` function is executed only when the script is run directly, not when imported as a module.

2. **Executing the Chatbot**:
   - **`main()`**:
     - Launches the chatbot application, allowing the user to interact with the AI and manage conversations.

3. **Resource Cleanup**:
   - **`finally:`**:
     - Ensures that the following resources are closed properly, regardless of whether an exception occurs:
     - **`cursor.close()`**:
       - Closes the database cursor to free up resources.
     - **`conn.close()`**:
       - Closes the database connection to prevent resource leaks.


```python
if __name__ == "__main__":
    try:
        main()
    finally:
        cursor.close()
        conn.close()
```


## Supplementary Files

### stream_chatbot/streamlit_app.py
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

**Previous**: [Mail E-Assistant](../email-e-assistant/mail-e-assistant.md) | **Next**: [Stream Chatbot > Memory Chabot](stream-chatbot/memory-chabot.md)
