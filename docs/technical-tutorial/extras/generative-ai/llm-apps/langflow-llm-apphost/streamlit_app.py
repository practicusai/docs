import practicuscore as prt
import streamlit as st
from langflow.load import run_flow_from_json

# The below will secure the page by authenticating and authorizing users with Single-Sign-On.
# Please note that security code is only activate when the app is deployed.
# Pages are always secure, even without the below, during development and only the owner can access them.
prt.apps.secure_page(
    page_title="Hello World App",
    must_be_admin=False,
)


def main():
    # The below is standard Streamlit code..
    st.title("My App on Practicus AI")

    st.markdown("##### Welcome to the front-end of your flow")

    # Initialize session state to store chat messages if not already initialized.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display all messages stored in session state in the chat interface.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # When the user inputs a message, add it to the chat history and display it.
    if prompt := st.chat_input("I'm your flow, how may I help you?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.write(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt)
                message_placeholder.write(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})


def run_flow(message, flow_json):
    result = run_flow_from_json(flow=flow_json, input_value=message, fallback_to_env_vars=True)  # False by default
    return result


# Function to generate a response from the flow based on the user's input.
def generate_response(prompt):
    # Log the user's question.
    # logging.info(f"question: {prompt}")

    # Run the flow to get the response.
    response = run_flow(message=prompt, flow_json="Flow.json")

    run_output = response[0]
    result_data = run_output.outputs[0]
    message_obj = result_data.results["message"]
    message_text = message_obj.data["text"]

    try:
        # Log and return the assistant's response.
        # logging.info(f"answer: {message_obj}")
        return message_text
    except Exception as exc:
        # Log any errors and return a fallback message.
        # logging.error(f"error: {exc}")
        return "Sorry, there was a problem finding an answer for you."


# Run the main function to start the Streamlit app.
if __name__ == "__main__":
    main()
