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

# Practicus AI Secrets with Built-in Vault

This notebook demonstrates how to work with Practicus AI’s built-in Vault to securely store, retrieve, and manage secrets. Practicus AI Vault offers encryption at rest, key rotation, and other security features to protect sensitive data.

## Overview
- **Create or Update a Secret:** You can create or update a personal secret, prompting for sensitive input rather than hardcoding it.
- **Retrieve a Secret:** Retrieve the stored secret along with its age in days.
- **Shared Secrets:** Access secrets marked as shared (useful if multiple team members or projects need a common secret).
- **Delete a Secret:** Remove the secret from the Vault if it’s no longer needed.


```python
import practicuscore as prt
from getpass import getpass

# Create or update a personal secret
personal_secret_name = "MY_PERSONAL_SECRET_1"
key = getpass(f"Enter key for {personal_secret_name}:")

prt.vault.create_or_update_secret(name=personal_secret_name, key=key)
```

## Retrieving the Personal Secret
Next, we fetch the secret we just stored in the Vault, ensuring it was saved correctly.

```python
key, age = prt.vault.get_secret(
    name=personal_secret_name,
)
print(f"Retrieved personal secret {personal_secret_name} key: ****, length is {len(key)} chars, which is {age} days old.")
```

## Accessing a Shared Secret
You can also retrieve secrets that are created by administrators and shared with you or one of your groups.

```python
shared_secret_name = "SHARED_SECRET_1"

key, age = prt.vault.get_secret(name=shared_secret_name, shared=True)
print(f"Retrieved shared secret {shared_secret_name} key: ****, length is {len(key)} chars, which is {age} days old.")
```

## Deleting a Secret
Finally, if you no longer need the secret, you can delete it from the Vault.

```python
prt.vault.delete_secret(name=personal_secret_name)
print(f"Deleted personal secret: {personal_secret_name}")
```


---

**Previous**: [Introduction](introduction.md) | **Next**: [Automated Worker Init](automated-worker-init.md)
