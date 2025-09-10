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

# Practicus AI Secrets with Built-in Vault

This notebook demonstrates how to work with Practicus AI’s built-in Vault to securely store, retrieve, and manage secrets. Practicus AI Vault offers encryption at rest, key rotation, and other security features to protect sensitive data.

## Overview
- **Create or Update a Secret:** You can create or update a personal secret, prompting for sensitive input rather than hardcoding it.
- **Retrieve a Secret:** Retrieve the stored secret along with its age in days.
- **Shared Secrets:** Access secrets marked as shared (useful if multiple team members or projects need a common secret).
- **Delete a Secret:** Remove the secret from the Vault if it’s no longer needed.


```python
personal_secret_name = "PERSONAL_SECRET_1"
shared_secret_name = "SHARED_SECRET_1"
automated_test = False

```

```python
assert personal_secret_name, "Please enter your personal_secret_name."
assert shared_secret_name, "Please enter your shared_secret_name."
```

```python
import practicuscore as prt
from getpass import getpass

# Create or update a personal secret
if not automated_test:
    key = getpass(f"Enter key for {personal_secret_name}:")
else:
    import secrets
    key = secrets.token_hex(16)

prt.vault.create_or_update_secret(name=personal_secret_name, key=key)
```

## Retrieving the Personal Secret
Next, we fetch the secret we just stored in the Vault, ensuring it was saved correctly.

```python
import practicuscore as prt

key, age = prt.vault.get_secret(
    name=personal_secret_name,
)
print(
    f"Retrieved personal secret {personal_secret_name} key: ****, length is {len(key)} chars, and it is {age} days old."
)
```

## Accessing a Shared Secret
You can also retrieve secrets that are created by administrators and shared with you or one of your groups.

```python
key, age = prt.vault.get_secret(name=shared_secret_name, shared=True)
print(f"Retrieved shared secret {shared_secret_name} key: ****, length is {len(key)} chars, and it is {age} days old.")
```

## Deleting a Secret
Finally, if you no longer need the secret, you can delete it from the Vault.

```python
prt.vault.delete_secret(name=personal_secret_name)
print(f"Deleted personal secret: {personal_secret_name}")
```

<!-- #region -->
## Using `prtcli` Terminal Commands (CLI)

You can also use Practicus AI Command Line Interface (CLI) `prtcli` to interact with Practicus AI Vault. 

### Retrieving a Personal Secret

To retrieve a personal secret from Practicus AI Vault, use the following command:

```bash
MY_SECRET=$(prtcli get-secret -p name="MY_SECRET")
```

This command assigns the output of `prtcli get-secret` to the environment variable `MY_SECRET`. If the secret is missing, the command will fail and nothing will be printed.

### Handling Errors

It's important to verify that the secret has been successfully retrieved before proceeding. Use the following snippet to exit your script if the secret is empty:

```bash
if [ -z "${MY_SECRET}" ]; then
    echo "ERROR: Could not retrieve secret named MY_SECRET. Please check your configuration." >&2
    exit 1
fi
```

This code checks if `MY_SECRET` is empty, and if so, prints an error message to stderr and exits with a non-zero status.

### Retrieving a Shared Secret

If you need to retrieve a shared secret saved via the Admin UI, include the `shared` parameter:

```bash
SHARED_SECRET=$(prtcli get-secret -p name="MY_SHARED_SECRET" shared=true)
```

Again, ensure that you verify the retrieval of the secret before proceeding:

```bash
if [ -z "${SHARED_SECRET}" ]; then
    echo "ERROR: Could not retrieve shared secret named MY_SHARED_SECRET. Please check your configuration." >&2
    exit 1
fi
```

### CLI Best Practices

- **Never print secrets:** Avoid printing secret values in production. Use environment variables for internal use only.
- **Always check for errors:** Validate that each secret is properly retrieved before continuing with your script.
- **Documentation:** Clearly document your usage of secrets and error handling in your scripts to help with troubleshooting.
<!-- #endregion -->


---

**Previous**: [Introduction](introduction.md) | **Next**: [Automated Init > Build](automated-init/build.md)
