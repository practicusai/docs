import practicuscore as prt
import streamlit as st

from shared.helper import some_function

# Since this page is not secured, it will be public after deployment.
# During development, it is still only accessible to the owner, and only from Practicus AI Studio.
# If the home page is secured, a public child page will only be accessible if directly requested.
# prt.apps.secure_page(
#     page_title="My second child page"
# )

st.title("My App on Practicus AI")

st.write("Hello from my second page!")
st.write("This page is not secured and will be open to public.")

st.write(some_function())

if "page_2_counter" not in st.session_state:
    st.session_state.page_2_counter = 0

increment = st.button("Increment Counter +4")
if increment:
    st.session_state.page_2_counter += 4

st.write("Counter = ", st.session_state.page_2_counter)
