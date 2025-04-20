import psycopg2
import datetime


def create_connection():
    try:
        connection = psycopg2.connect(
            host="test-db-1.c34rytcb0n56.us-east-1.rds.amazonaws.com",
            database="llm",
            user="prt_analytics_user",
            password="",
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
            cursor.execute(
                "INSERT INTO sessions (session_id, title, created_at, language) VALUES (%s, %s, %s, %s)",
                (session_id, f"Session - {session_id[:8]}", now, "English"),
            )

            connection.commit()

        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)", (session_id, role, content)
        )
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


def update_message_in_db(session_id, old_content, new_content):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE messages 
            SET content = %s 
            WHERE session_id = %s AND content = %s
        """,
            (new_content, session_id, old_content),
        )
        connection.commit()
        cursor.close()
        connection.close()
