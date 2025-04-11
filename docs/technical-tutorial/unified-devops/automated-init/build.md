---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Automated Initialization of Workers and Applications with Secrets

This example demonstrates how to pass custom configuration as OS environment variables along with secure secrets from the Practicus AI Vault (both personal and shared) to a Practicus AI Worker and an Application. This method allows you to configure necessary settings at startup without hardcoding sensitive data.

## Key Concepts
- **Environment Variables:** Regular OS-level variables available to the worker or app.
- **Personal Secrets:** Private secrets that are injected as environment variables.
- **Shared Secrets:** Secrets that can be shared across projects or team members, also injected as environment variables. These are only defined by an admin, and using Practicus AI admin console.
- **Worker Interaction:** After launching a worker and opening a notebook on it, you can verify that the environment variables and secrets have been set correctly. (Remember: never log or display actual secret values in production!)

## Worker Initialization

```python
worker_size = None
app_deployment_key = None
app_prefix = "apps"
```

```python
assert worker_size, "Please enter your worker_size."
assert app_deployment_key, "Please select an app deployment setting."
assert app_prefix, "Please select an app prefix."
```

```python
import practicuscore as prt

# Configure the worker with environment variables and secrets
worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    env_variables={
        "MY_FIRST_ENV": "123",  # Standard environment variable as a string
        "MY_SECOND_ENV": 123,  # Standard environment variable as a number
    },
    personal_secrets=["PERSONAL_SECRET_1"],  # Personal secret (injected as an environment variable)
    shared_secrets=["SHARED_SECRET_1"],  # Shared secret (injected as an environment variable)
)

# Create and start the worker
worker = prt.create_worker(worker_config)

# Open a Jupyter notebook on the newly created worker
worker.open_notebook()
```

<!-- #region -->
## Verifying Environment Variables and Secrets

To confirm that the environment variables and secrets have been injected correctly, open the worker’s terminal (not in this notebook) and run the following commands:

```bash
echo "MY_FIRST_ENV is: $MY_FIRST_ENV"
echo "MY_SECOND_ENV is: $MY_SECOND_ENV"
# For security, only check the length of secret values instead of printing them
echo "PERSONAL_SECRET_1 length:" $(echo $PERSONAL_SECRET_1 | wc -m)
echo "SHARED_SECRET_1 length:" $(echo $SHARED_SECRET_1 | wc -m)
```

These commands ensure that the worker’s environment is configured correctly without revealing sensitive information.
<!-- #endregion -->

```python
# Terminate the worker when you are done
worker.terminate()
```

## App Initialization

Similar to workers, you can also deploy an Application with environment variables and secrets. In this example, the App includes an API (defined in `apis/verify.py`) that returns the current configuration for verification.

```python
# Need help finding app deployment settings and prefixes?
# You can retrieve available app deployment settings and prefixes
import practicuscore as prt

region = prt.get_region()
my_app_settings = prt.apps.get_deployment_setting_list()

print("Available Application Deployment Settings:")
display(my_app_settings.to_pandas())

my_app_prefixes = prt.apps.get_prefix_list()

print("Available Application Prefixes:")
display(my_app_prefixes.to_pandas())
```

```python
import practicuscore as prt

app_name = "my-auto-configured-app"
visible_name = "My Auto Configured App"
description = "This application is configured with environment variables and secrets."
icon = "check"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    startup_script="echo 'hello' > hello.txt",
    env_variables={"MY_FIRST_ENV": "123", "MY_SECOND_ENV": 123},
    personal_secrets=["PERSONAL_SECRET_1"],
    shared_secrets=["SHARED_SECRET_1"],
    icon=icon,
)

print("Launching UI at:", app_url)
print("Launching API at:", api_url)
```

```python
# Verify the App's configuration by calling its API
import requests

# Retrieve a session token for authentication
token = prt.apps.get_session_token(api_url=api_url)
verify_api_url = f"{api_url}verify/"

headers = {
    "Authorization": f"Bearer {token}",
}

print("Requesting verification from:", verify_api_url)
resp = requests.get(verify_api_url, headers=headers)

if resp.ok:
    resp_json = resp.json()
    print("Configuration received:", resp_json)

    print("Validating configuration values...")
    # Check that both environment variables have the expected value
    assert resp_json["MY_FIRST_ENV"] == resp_json["MY_SECOND_ENV"] == "123"
    # Verify that the secrets are present by checking their lengths
    assert resp_json["PERSONAL_SECRET_1_LEN"] > 0
    assert resp_json["SHARED_SECRET_1_LEN"] > 0
    # Confirm that the startup script executed correctly
    assert resp_json["hello_txt_content"] == "hello"
    print("Configuration validated successfully.")
else:
    print("Error during API verification:", resp.status_code, resp.text)
```

```python
# Cleanup: Delete the deployed App when finished
import practicuscore as prt

region = prt.get_region()
prt.apps.delete(prefix=app_prefix, app_name=app_name)
```

## Customizing Secret OS Environment Variable Names

You can rename the environment variable used to inject a secret by using the `name:other_name` format. For example:

- Specifying `"PERSONAL_SECRET_1:SOME_ENV_NAME"` will look up the secret with the name `PERSONAL_SECRET_1` and inject it into the environment as `SOME_ENV_NAME`.
- Similarly, `"SHARED_SECRET_1:OTHER_ENV_NAME"` retrieves the secret `SHARED_SECRET_1` and makes it available as `OTHER_ENV_NAME`.

This format is supported for both personal and shared secrets, enabling you to avoid naming conflicts and integrate the secrets seamlessly into your application or worker configuration.



## Supplementary Files

### apis/verify.py
```python
import os
import practicuscore as prt


MY_FIRST_ENV = os.getenv("MY_FIRST_ENV", default="?")
MY_SECOND_ENV = os.getenv("MY_SECOND_ENV", default="?")
PERSONAL_SECRET_1 = os.getenv("PERSONAL_SECRET_1", default="?")
SHARED_SECRET_1 = os.getenv("SHARED_SECRET_1", default="?")
# All Practicus AI apps boot at /var/practicus, and your files are copied here.
HELLO_TXT_PATH = "/var/practicus/hello.txt"


@prt.apps.api("/verify")
async def verify(**kwargs):
    hello_txt_content = "?"
    if os.path.exists(HELLO_TXT_PATH):
        with open(HELLO_TXT_PATH, "r") as f:
            hello_txt_content = f.read().strip()

    return {
        "msg": "Reading configuration from OS environment variables. (Only length of secrets for security)",
        "MY_FIRST_ENV": MY_FIRST_ENV,
        "MY_SECOND_ENV": MY_SECOND_ENV,
        "PERSONAL_SECRET_1_LEN": len(PERSONAL_SECRET_1),
        "SHARED_SECRET_1_LEN": len(SHARED_SECRET_1),
        "hello_txt_content": hello_txt_content,
    }

```


---

**Previous**: [Secrets With Vault](../secrets-with-vault.md) | **Next**: [Automated Git Sync](../automated-git-sync.md)
