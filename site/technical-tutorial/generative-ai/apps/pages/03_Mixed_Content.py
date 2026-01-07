import practicuscore as prt
import streamlit as st

prt.apps.st.secure_page(
    page_title="Mixed content page",
)

st.title("Mixed content page")

st.write("Everyone will see this part of the page.")
st.write("If you see nothing below, you are not an admin.")


# Only admins will see this
if prt.apps.st.user_is_admin():
    st.subheader("Admin Section")
    st.write("If you see this part, you are an admin, owner of the app, or in development mode.")

    # Input fields
    admin_input1 = st.text_input("Admin Input 1")
    admin_input2 = st.text_input("Admin Input 2")

    admin_action = st.button("Admin Button")
    if admin_action:
        st.write("Performing some dummy admin action..")
