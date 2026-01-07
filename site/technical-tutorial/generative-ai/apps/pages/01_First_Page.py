import practicuscore as prt
import streamlit as st

from shared.helper import some_function

# Child pages must also request to be secured.
# Or else, they will be accessible by everyone after deployment.

prt.apps.st.secure_page(
    page_title="My first child page",
)

st.title("My App on Practicus AI")

st.write("Hello from first page!")

st.write(some_function())

if "page_1_counter" not in st.session_state:
    st.session_state.page_1_counter = 0

increment = st.button("Increment Counter +2")
if increment:
    st.session_state.page_1_counter += 2

st.write("Counter = ", st.session_state.page_1_counter)
