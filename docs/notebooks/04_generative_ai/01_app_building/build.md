---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus GenAI
    language: python
    name: practicus_genai
---

```python
import practicuscore as prt
```

```python
prt.apps.test_app()
```

```python
import apis.say_hello
from apis.say_hello import Person, SayHelloRequest, SayHelloResponse

person = Person(
    name="Alice", 
    email="alice@wonderland.com"
)

payload = SayHelloRequest(
    person=person
)
from pydantic import BaseModel

print(issubclass(type(payload), BaseModel))

response: SayHelloResponse = prt.apps.call_api(apis.say_hello, payload)

print("Greeting message:", response.greeting_message)
print("Email:", response.for_person.email)
```

```python
region = prt.get_region()

my_app_settings = region.app_deployment_setting_list
assert len(my_app_settings) > 0, "I don't have access to any app deployment settings!"

print("Application deployment settings I have access to:") 
display(my_app_settings.to_pandas())

deployment_setting_key = my_app_settings[0].key
print("Using first setting with key:", deployment_setting_key)
```

```python
my_app_prefixes = region.app_prefix_list
assert len(my_app_prefixes) > 0, "I don't have access to any app prefix!"

print("Application prefixes (groups) I have access to:") 
display(my_app_prefixes.to_pandas())

prefix = my_app_prefixes[0].prefix
print("Using first app prefix with key:", prefix)
```

```python
app_name="my-first-app"
# The below are optional, but recommended fields
visible_name = "My First App",
description = "A very useful app..",
# Font awesome 6 short icon name, or full class name e.g. fa-solid fa-rocket
# You can find an icon at https://fontawesome.com/icons 
# Please select "Free" icons only and not the "pro" ones.
icon = "rocket",  

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=deployment_setting_key,
    prefix=prefix,
    app_name=app_name,
    app_dir=None, # Current dir
    visible_name=visible_name,
    description=description,
    icon=icon,
)
```

### Understanding versions
- You can use the UI App and API URLs wihtout the version part. 
- E.g. instead of https://practicus.company.com/apps/my-first-app/v3/ you can use https://practicus.company.com/apps/my-first-app/ and the traffic will route to the correct version automatically.
#### Automated traffic routing
- You can also access different versions like the below, or let the system decide routing.
- Let the system decide: https://practicus.company.com/apps/my-first-app/
- The traffic routes to the latest version OR the production version if an admin marked a version as prod.
- Production: https://practicus.company.com/apps/my-first-app/prod/
- Staging: https://practicus.company.com/apps/my-first-app/staging/
- Latest: https://practicus.company.com/apps/my-first-app/latest/
- Specific version: https://practicus.company.com/apps/my-first-app/v[version]/
- The above applies to both UI App and API URLs.

```python
import requests 

# Get a short-lived session token using Practicus AI SDK.
token = prt.apps.get_session_token(api_url=api_url)

# You can also ask an admin to create a long-lived access token for this app,
#   or all apps under a certain app prefix, e.g. apps/finance/* 
#   With this option, a developer can use your APIs without Practicus AI SDK.

say_hello_api_url = f"{api_url}say-hello/"

headers = {
    "Authorization": f"Bearer {token}",
    "content-type": 'application/json'}

json=payload.model_dump_json(indent=2)
print(f"Sending below JSON to: {say_hello_api_url}")
print(json)

resp = requests.post(say_hello_api_url, json=json, headers=headers)

if resp.ok:
    print("Response text:")
    print(resp.text)
    response_obj = SayHelloResponse.model_validate_json(resp.text)
    print("Response object:")
    print(response_obj)
else:
    print("Error:", resp.status_code, resp.text)
```

### Deleting Apps / App Versions

You can delete:
- An app, which will delete all of the versions (deployment) of the app.
- A particular app version. Note: you cannot delete the latest version.

To have **delete permissions** on an app or one of it's versions, you need one of the following:

- Be the owner (creator) of the app. Note: A system admin can change the owner of an app after it is created.
- Have admin privileges for the app's prefix. E.g. If you are an admin for the prefix "apps/finance/test" you can override / delete all apps under this prefix e.g. "apps/finance/test/some-other-users-app"
- Be a system admin (superuser). 

```python
print("Listing all the apps and their versions I have access to:")
region.app_list.to_pandas()
```

```python
# Deleting an app and all it's versions
region.delete_app(app_id=123)
# If you don't know the app_id you can use prefix and app_name
region.delete_app(prefix="apps", app_name="my-first-app")
```

```python
# Deleting a particular version of an app
region.delete_app_version(app_id=123, version=4)
# If you don't know the app_id you can use prefix and app_name
region.delete_app_version(prefix="apps", app_name="my-first-app", version=4)
```


## Supplementary Files

### Home.py
```python
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

```

### apis/say_hello.py
```python
from pydantic import BaseModel


class Person(BaseModel):
    name: str
    email: str | None = None


class SayHelloRequest(BaseModel):
    person: Person


class SayHelloResponse(BaseModel):
    greeting_message: str
    for_person: Person


def run(payload: SayHelloRequest, **kwargs):
    return SayHelloResponse(greeting_message=f"Hello {payload.person.name}", for_person=payload.person)

```

### pages/01_First_Page.py
```python
import practicuscore as prt
import streamlit as st

from shared.helper import some_function

# Child pages must also request to be secured.
# Or else, they will be accessible by everyone after deployment.

prt.apps.secure_page(
    page_title="My first child page",
)

st.title("My App on Practicus AI")

st.write("Hello from first page!")

st.write(some_function())

if 'page_1_counter' not in st.session_state:
    st.session_state.page_1_counter = 0

increment = st.button('Increment Counter +2')
if increment:
    st.session_state.page_1_counter += 2

st.write('Counter = ', st.session_state.page_1_counter)

```

### pages/02_Second_Page.py
```python
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

if 'page_2_counter' not in st.session_state:
    st.session_state.page_2_counter = 0

increment = st.button('Increment Counter +4')
if increment:
    st.session_state.page_2_counter += 4

st.write('Counter = ', st.session_state.page_2_counter)

```

### pages/03_Mixed_Content.py
```python
import practicuscore as prt
import streamlit as st

prt.apps.secure_page(
    page_title="Mixed content page",
)

st.title("Mixed content page")

st.write("Everyone will see this part of the page.")
st.write("If you see nothing below, you are not an admin.")


# Only admins will see this
if prt.apps.user_is_admin():
    st.subheader("Admin Section")
    st.write("If you see this part, you are an admin, owner of the app, or in development mode.")

    # Input fields
    admin_input1 = st.text_input("Admin Input 1")
    admin_input2 = st.text_input("Admin Input 2")

    admin_action = st.button('Admin Button')
    if admin_action:
        st.write("Performing some dummy admin action..")
    
```

### pages/04_Cookies.py
```python
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


```

### pages/05_App_Meta.py
```python
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

```

### pages/06_Settings.py
```python
import practicuscore as prt
import streamlit as st

# User must have admin privileges to view this page (must_be_admin=True)
prt.apps.secure_page(
    page_title="Settings Page",
    must_be_admin=True,
)

st.title("Settings page")

st.write("If you see this, you are an admin, owner of the app, or in development mode.")

```

### shared/helper.py
```python
def some_function():
    return "And, this text is from a shared function."

```


---

**Previous**: [AI Studio](../../03_workflows/03_AI_Studio/AI_Studio.md) | **Next**: [Langchain With Streaming](../02_langchain/langchain_with_streaming.md)
