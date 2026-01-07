import practicuscore as prt
import streamlit as st

# User must have admin privileges to view this page (must_be_admin=True)
prt.apps.st.secure_page(
    page_title="Settings Page",
    must_be_admin=True,
)

st.title("Settings page")

st.write("If you see this, you are an admin, owner of the app, or in development mode.")
