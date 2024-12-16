import practicuscore as prt
import streamlit as st

from shared.helper import some_function

# The below will secure the page by authenticating and authorizing users with Single-Sign-On.
# Please note that security code is only activate when the app is deployed.
# Pages are always secure, even without the below, during development and only the owner can access them.
prt.apps.secure_page(
    page_title="Hello World App",
    must_be_admin=False,
)

# The below is standard Streamlit code..
st.title("My App on Practicus AI")

st.write("Hello!")
st.write("This is a text from the code inside the page.")

st.write(some_function())

if 'counter' not in st.session_state:
    st.session_state.counter = 0

increment = st.button('Increment Counter')
if increment:
    current = st.session_state.counter
    new = current + 1
    st.session_state.counter = new
    prt.apps.logger.info(f"Increased counter from {current} to {new}")

st.write('Counter = ', st.session_state.counter)
