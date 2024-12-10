import practicuscore as prt
import streamlit as st

prt.apps.secure_page(
    page_title="Application Metadata"
)

st.title("Application Metadata")

if prt.apps.development_mode():
    st.subheader("Development Mode")
    st.markdown(
        """
        You are in **development mode**, and application metadata is only available after deploying the app.

        **Developer Information:**
        """
    )
    st.write({
        "Email": prt.apps.get_user_email(),
        "Username": prt.apps.get_username(),
        "User ID": prt.apps.get_user_id(),
    })
else:
    st.subheader("Deployed App Metadata")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Application Details**")
        st.write({
            "Name": prt.apps.get_app_name(),
            "Prefix": prt.apps.get_app_prefix(),
            "Version": prt.apps.get_app_version(),
            "App ID": prt.apps.get_app_id(),
        })

    with col2:
        st.markdown("**User Information**")
        st.write({
            "Email": prt.apps.get_user_email(),
            "Username": prt.apps.get_username(),
            "User ID": prt.apps.get_user_id(),
        })

if st.button("View User Groups"):
    st.write(
        prt.apps.get_user_groups()
    )
    # User groups are cached. If you need reset you can call:
    # reload = True
    # prt.apps.get_user_groups(reload)
