---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region -->
# Building and Managing Applications with Practicus AI

Practicus AI enables the development, deployment, and management of secure, enterprise-grade visual applications built on [Streamlit](https://docs.streamlit.io/). While Streamlit itself is a simple framework for creating interactive, web-based apps, Practicus AI provides enterprise-level features on top of it:

* **Enterprise Single Sign-On (SSO)** integration with LDAP or other enterprise authentication methods.
* **User and Group-Based Customization**: Dynamically tailor pages and content based on user roles and permissions.
* **Administrative Pages**: Add interfaces to manage users, groups, and application settings.
* **Version and Traffic Management**: Seamlessly handle multiple versions of your app, route traffic to staging or production, and roll out changes gradually.

This example demonstrates how to leverage Practicus AI to deploy a basic Streamlit app, integrate it with APIs, and manage it with enterprise security and versioning features.


### Sample Streamlit Application Overview

This sample Streamlit application demonstrates a variety of features and best practices for building secure, multi-page apps within the Practicus AI environment. It includes the following components:

**Home.py:** The main entry point that authenticates and authorizes users, sets a page title, and displays a basic counter. It illustrates how to secure pages in both development and production modes.
  
**pages/**: A collection of additional Streamlit pages showcasing different functionalities:

- **01_First_Page.py:** A secured child page with its own counter.
- **02_Second_Page.py:** A non-secured page accessible publicly when deployed.
- **03_Mixed_Content.py:** A page demonstrating mixed access levels, where certain sections are only visible to administrators.
- **04_Cookies.py:** A page handling cookie creation, retrieval, and deletion.
- **05_App_Meta.py:** A page displaying application metadata and user details, differing in development vs. deployed scenarios.
- **06_Settings.py:** An admin-only settings page.

**apis/**:

- **say_hello.py:** A simple API endpoint that returns a personalized greeting.

**shared/helper.py:** Contains reusable helper functions for shared logic.

This sample code serves as a reference for building, testing, and deploying secure, multi-page Streamlit apps on Practicus AI, with integrated authentication, logging, and developer-focused features.
<!-- #endregion -->

### Defining parameters.

This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.

```python
app_deployment_key = "appdepl"
app_prefix = "apps"

test_ui = True
test_api = True
```

If you don't know your prefixes and deployments you can check them out by using the SDK like down below:

```python
import practicuscore as prt

my_app_settings = prt.apps.get_deployment_setting_list()

print("Application deployment settings I have access to:")
display(my_app_settings.to_pandas())

my_app_prefixes = prt.apps.get_prefix_list()

print("Application prefixes (groups) I have access to:")
display(my_app_prefixes.to_pandas())
```

```python
assert app_deployment_key, "Please select an app deployment setting."
assert app_prefix, "Please select an app prefix."
```

### Before You Continue

To ensure proper execution, run the code below on a Practicus AI GenAI or a compatible container image. Make sure to use the GenAI Jupyter kernel (the `practicus_genai` virtual environment).

### (Recommended) Testing Application UIs in Design Time

You can launch a sample Streamlit application directly within the Practicus AI worker to test it before deploying to a Practicus AI AppHost system.

#### Testing on VS Code

If you are using VS Code, click on the printed URL to view the application.

#### Testing on Jupyter

If you are using Jupyter, we recommend using Practicus AI Studio, which has built-in GenAI app visualization. After running the code below, navigate to **Explore**, right-click on the worker, and select **GenAI App**.

```python
if test_ui:
    prt.apps.test_app()
```

### (Recommended) Testing APIs in design time

```python
if test_api:
    from apis.say_hello import Person, SayHelloRequest, SayHelloResponse
    from pydantic import BaseModel

    person = Person(name="Alice", email="alice@wonderland.com")
    payload = SayHelloRequest(person=person)

    print(issubclass(type(payload), BaseModel))

    response: SayHelloResponse = prt.apps.test_api("/say-hello", payload)
    print("Greeting message:", response.greeting_message)
```

### (Recommended) Analyze the App before deployment

```python
prt.apps.analyze()
```

## Deploying the App

Once our development and tests are over, we can deploy the app as a new version.

```python
app_name = "my-first-app"
visible_name = "My First App"
description = "A very useful app.."
icon = "fa-rocket"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("Booting UI :", app_url)
print("Booting API:", api_url)
print("API Docs   :", api_url + "redoc/")
```

### Understanding App Versions

Practicus AI supports multiple app versions and provides different URLs for each environment:

* Default route: `https://practicus.company.com/apps/my-first-app/` routes to the latest or production version.
* Specific versions:
  * Production: `/prod/`
  * Staging: `/staging/`
  * Latest: `/latest/`
  * Exact version: `/v[version]/`
  * For Practicus AI API service mesh dynamically routes to work, place `version indicator right after /api/`
  * For example:
  * https://practicus.company.com/apps/my-first-app/api/prod/say-hello/
  * https://practicus.company.com/apps/my-first-app/api/v4/say-hello/
  * Please note that ../api/say-hello/v4/ or ../api/say-hello/v4/prod/ will **not** work.


```python
import requests

token = None  # Get a new token, or reuse existing, if not expired
token = prt.apps.get_session_token(api_url=api_url, token=token)
say_hello_api_url = f"{api_url}say-hello/"

headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}

json_data = payload.model_dump_json(indent=2)
print(f"Sending below JSON to: {say_hello_api_url}")
print(json_data)

resp = requests.post(say_hello_api_url, json=json_data, headers=headers)

if resp.ok:
    print("Response text:")
    print(resp.text)
    response_obj = SayHelloResponse.model_validate_json(resp.text)
    print("Response object:")
    print(response_obj)
else:
    print("Error:", resp.status_code, resp.text)
```

### Deleting Apps or App Versions

You can delete entire apps or specific versions if you have the appropriate permissions:

* Delete an app: removes all versions.
* Delete a particular version: cannot delete the latest version.

Permissions can be granted by:

* Being the app owner.
* Having admin privileges for the app's prefix.
* Being a system admin.

```python
print("Listing all apps and their versions I have access to:")
prt.apps.get_list().to_pandas()
```

```python
# If you don't know the app_id you can use prefix and app_name
prt.apps.delete(prefix=app_prefix, app_name=app_name)

try:
    # Deleting an app and all it's versions
    prt.apps.delete(app_id=123)
except:
    pass
```

```python
try:
    # Deleting a particular version of an app
    prt.apps.delete_version(app_id=123, version=4)

    # If you don't know the app_id you can use prefix and app_name
    prt.apps.delete_version(prefix="apps", app_name="my-first-app", version=4)
except:
    pass
```


#### Note on Startup Scripts

You can use the `startup_script` parameter with `prt.apps.deploy` for basic configuration tasks. **Do not** use `startup_script` to install packages, including pip. Application hosting runs in a different security context from Workers (which are designed for design-time and batch tasks). To install packages, create a new container image instead. See the **Unified DevOps** section for instructions on building container images.


## Supplementary Files

### Home.py
```python
import practicuscore as prt
import streamlit as st

from shared.helper import some_function
# If you are using init_app.py, unlike APIs, you must manually load like the below for UI.
# import init_app  # noqa

# The below will secure the page by authenticating and authorizing users with Single-Sign-On.
# Please note that security code is only activate when the app is deployed.
# Pages are always secure, even without the below, during development and only the owner can access them.
prt.apps.st.secure_page(
    page_title="Hello World App",
    must_be_admin=False,
)

# The below is standard Streamlit code..
st.title("My App on Practicus AI")

st.write("Hello!")
st.write("This is a text from the code inside the page.")

st.write(some_function())

if "counter" not in st.session_state:
    st.session_state.counter = 0

increment = st.button("Increment Counter")
if increment:
    current = st.session_state.counter
    new = current + 1
    st.session_state.counter = new
    prt.logger.info(f"Increased counter from {current} to {new}")

st.write("Counter = ", st.session_state.counter)

```

### apis/say_hello.py
```python
from pydantic import BaseModel
import practicuscore as prt


class Person(BaseModel):
    name: str
    """Name of the Person"""
    email: str | None = None
    """Email of the Person"""

    model_config = {
        "use_attribute_docstrings": True,
    }


class SayHelloRequest(BaseModel):
    person: Person
    """Person to say hello to"""

    # Optional configuration
    model_config = {
        # use_attribute_docstrings=True allows documentation with """add docs here""" format
        # Alternative is to use Field(..., description="add docs here"
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            # Examples get documented in OpenAPI and are extremely useful for AI Agents.
            "examples": [
                {"person": {"name": "Alice", "email": "alice@wonderland.com"}},
                {"person": {"name": "Bill", "email": "bill@wonderland.com"}},
            ]
        },
    }


class SayHelloResponse(BaseModel):
    greeting_message: str
    """Greeting message"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"greeting_message": "Hello Alice"}, {"greeting_message": "Hello Bill"}]},
    }


@prt.api("/say-hello")
async def say_hello(payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """This API sends a greeting message back to the caller"""

    return SayHelloResponse(greeting_message=f"Hello {payload.person.name}")


# An API example custom spec (metadata)
# These get documented in OpenAPI (Swagger) format and can be made available dynamically to AI Agents
api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.AIAgent,
    read_only=False,
    scope=prt.APIScope.TeamWide,
    risk_profile=prt.APIRiskProfile.High,
    human_gated=True,
    deterministic=False,
    idempotent=False,
    stateful=True,
    asynchronous=True,
    maturity_level=4,
    disable_authentication=True,
    # Primitive types (int, str etc) are recommended for custom attributes.
    custom_attributes={
        "my-cust-attr-str": "hello",
        "my-cust-attr-int": 123,
        "my-cust-attr-float": 1.2,
        "my-cust-attr-bool": True,
    },
)


@prt.api("/say-hello-with-spec", spec=api_spec)
async def say_hello_with_spec(request, payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """This API also sends a greeting message back to the caller, but with additional metadata for governance."""

    # Notes:
    # - You can add `request` as a param, which will be the FastAPI (Starlette) request object.
    # - Always add `**kwargs` to your function params since there can be a dynamic number of parameters passed.
    #   E.g., `requester: dict` includes the requesting user related info.
    # - You can access shared global state set in `init_app.py` E.g.,
    #   from shared.helper import AppState
    #   some_global_state = AppState.shared_variable
    #   prt.logger.info(f"Current global state: {some_global_state}")

    return SayHelloResponse(greeting_message=f"Hello2 {payload.person.name}")

```

### init_app.py
```python
# This file is automatically executed when your APIs App starts up.
# Use it to prepare global state, initialize resources, or connect to services.

# For UI apps, you must manually run `import init_app` in Home.py
# Please keep in mind that global state is *NOT* shared between the UI and API apps.
#   Home.py is a Streamlit App, APIs are hosted via FastAPI.

import practicuscore as prt
from shared.helper import AppState


def initialize() -> None:
    # Log that we are starting initialization
    prt.logger.info("Starting to initialize app.")

    # Example: change a global variable so all APIs can see the new value
    AppState.shared_variable = "changed"

    # Log that initialization is done
    prt.logger.info("Completed initializing app.")


# Run the initializer immediately on import
initialize()

```

### pages/01_First_Page.py
```python
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

```

### pages/02_Second_Page.py
```python
import practicuscore as prt
import streamlit as st

from shared.helper import some_function

# Since this page is not secured, it will be public after deployment.
# During development, it is still only accessible to the owner, and only from Practicus AI Studio.
# If the home page is secured, a public child page will only be accessible if directly requested.
# prt.apps.st.secure_page(
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

```

### pages/03_Mixed_Content.py
```python
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

```

### pages/04_Cookies.py
```python
import practicuscore as prt
import streamlit as st

# Secure the page using the provided SDK
prt.apps.st.secure_page(page_title="Using Cookies")

st.title("Cookies Management")

# Inputs for cookie operations
cookie_name = st.text_input("Cookie Name", placeholder="Enter cookie name")
cookie_value = st.text_input("Cookie Value", placeholder="Enter cookie value")
max_age = st.number_input(
    "Max Validity (seconds)", min_value=None, value=None, step=60, placeholder="Leave empty for 30 days"
)
path = st.text_input("Cookie path", placeholder="Leave empty for /")

# Add Cookie
if st.button("Add Cookie"):
    if cookie_name and cookie_value:
        prt.apps.st.set_cookie(name=cookie_name, value=cookie_value, max_age=max_age, path=path)
        st.success(f"Cookie '{cookie_name}' has been set!")
    else:
        st.error("Please provide both a cookie name and value.")

# Get Cookie Value
if st.button("Get Cookie Value"):
    if cookie_name:
        cookie_value = prt.apps.st.get_cookie(name=cookie_name)
        if cookie_value:
            st.success(f"The value of cookie '{cookie_name}' is: {cookie_value}")
        else:
            st.warning(f"No cookie found with the name '{cookie_name}'.")
    else:
        st.error("Please provide a cookie name to retrieve its value.")

# Delete Cookie
if st.button("Delete Cookie"):
    if cookie_name:
        prt.apps.st.delete_cookie(name=cookie_name)
        st.success(f"Cookie '{cookie_name}' has been deleted!")
    else:
        st.error("Please provide a cookie name to delete.")

```

### pages/05_App_Meta.py
```python
import practicuscore as prt
import streamlit as st

prt.apps.st.secure_page(page_title="Application Metadata")

st.title("Application Metadata")

if prt.apps.st.development_mode():
    st.subheader("Development Mode")
    st.markdown(
        """
        You are in **development mode**, and application metadata is only available after deploying the app.

        **Developer Information:**
        """
    )
    st.write(
        {
            "Email": prt.apps.st.get_user_email(),
            "Username": prt.apps.st.get_username(),
            "User ID": prt.apps.st.get_user_id(),
        }
    )
else:
    st.subheader("Deployed App Metadata")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Application Details**")
        st.write(
            {
                "Name": prt.apps.st.get_app_name(),
                "Prefix": prt.apps.st.get_app_prefix(),
                "Version": prt.apps.st.get_app_version(),
                "App ID": prt.apps.st.get_app_id(),
            }
        )

    with col2:
        st.markdown("**User Information**")
        st.write(
            {
                "Email": prt.apps.st.get_user_email(),
                "Username": prt.apps.st.get_username(),
                "User ID": prt.apps.st.get_user_id(),
            }
        )

if st.button("View User Groups"):
    st.write(prt.apps.get_user_groups())
    # User groups are cached. If you need reset you can call:
    # reload = True
    # prt.apps.get_user_groups(reload)

```

### pages/06_Settings.py
```python
import practicuscore as prt
import streamlit as st

# User must have admin privileges to view this page (must_be_admin=True)
prt.apps.st.secure_page(
    page_title="Settings Page",
    must_be_admin=True,
)

st.title("Settings page")

st.write("If you see this, you are an admin, owner of the app, or in development mode.")

```

### shared/helper.py
```python
# You can hold "global" state that can be shared across your APIs, and UI pages.
# You might use this for database connections, caches, or config.
# Keep in mind that global state is simple but also has tradeoffs:
#   - It is shared by all requests and all APIs
#   - You must be careful about concurrency and mutability


class AppState:
    # A trivial shared variable (string) with a default value.
    # Any API or initialization code can read or overwrite this.
    shared_variable: str = "empty"


def some_function():
    return "And, this text is from a shared function."

```


---

**Previous**: [Introduction](../introduction.md) | **Next**: [Model Serving > LLM > Model Serving](../model-serving/llm/model-serving.md)
