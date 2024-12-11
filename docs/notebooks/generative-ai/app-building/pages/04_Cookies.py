import practicuscore as prt
import streamlit as st

# Secure the page using the provided SDK
prt.apps.secure_page(
    page_title="Using Cookies"
)

st.title("Cookies Management")

# Inputs for cookie operations
cookie_name = st.text_input("Cookie Name", placeholder="Enter cookie name")
cookie_value = st.text_input("Cookie Value", placeholder="Enter cookie value")
max_age = st.number_input("Max Validity (seconds)", min_value=None, value=None, step=60, placeholder="Leave empty for 30 days")
path = st.text_input("Cookie path", placeholder="Leave empty for /")

# Add Cookie
if st.button("Add Cookie"):
    if cookie_name and cookie_value:
        prt.apps.set_cookie(name=cookie_name, value=cookie_value, max_age=max_age, path=path)
        st.success(f"Cookie '{cookie_name}' has been set!")
    else:
        st.error("Please provide both a cookie name and value.")

# Get Cookie Value
if st.button("Get Cookie Value"):
    if cookie_name:
        cookie_value = prt.apps.get_cookie(name=cookie_name)
        if cookie_value:
            st.success(f"The value of cookie '{cookie_name}' is: {cookie_value}")
        else:
            st.warning(f"No cookie found with the name '{cookie_name}'.")
    else:
        st.error("Please provide a cookie name to retrieve its value.")

# Delete Cookie
if st.button("Delete Cookie"):
    if cookie_name:
        prt.apps.delete_cookie(name=cookie_name)
        st.success(f"Cookie '{cookie_name}' has been deleted!")
    else:
        st.error("Please provide a cookie name to delete.")

