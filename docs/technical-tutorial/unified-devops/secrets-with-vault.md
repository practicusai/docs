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

<!-- #region -->
## Big secrets

Max secret key length is 2000 characters after encryption, which will give you around 1000-1250 characters to use as keys. 

For secrets such as SSL keys, this might not be enough. You can split the secret into multiple parts as seen below if you ever hit max secret size limit.

```python
import practicuscore as prt

long_secret = """-----BEGIN CERTIFICATE-----
MIIFJzCCAw+gAwIBAgIUyqlBgM2m9t3rfiyEGyuGkx8E4QgwDQYJKoZIhvcNAQEL
BQAwIzEhMB8GA1UEAwwYUHJhY3RpY3VzIEFJIFNlbGYtU2lnbmVkMB4XDTI0MTAx
MTIwNTYzNVoXDTM0MTAwOTIwNTYzNVowIzEhMB8GA1UEAwwYUHJhY3RpY3VzIEFJ
IFNlbGYtU2lnbmVkMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArpGo
vTOX8jzzuxt7QyycpStU64fe7o6dVMTRR2FVxv4xsnAQ5OmHXSaBhQtz4fTgq2hE
E9GrzEMBzpaI+zIe3kvxP3Rs/GvPr62x8ne/uaQdH214a+SlyDnn0SDPnF98zhHQ
Au+RWdCY1f+T0aDaNDI7kyHobJUga+7hGUyskaphR2UekFGsBI/unr/cFTa2LkVN
eDPTOTgurFpjR+TFe4cJ1nNO4c8ZzUpBkBZQf2kh5SJitniXsSQuD69e/Iajm+Ub
sCJfRGKhRRUdv06WbGOVNrmaU6MORLlX7lUvWSUKuPJOYXZJpg9qmh0ui3Gkfz9b
F0LBTzOKl+XEet5HccSWbn4ZnbAOaA/YHG5/FRCRWuMG8qNT2nAqc0HMYUkolN+x
TagCjcnxT1WqSXzcsAcMYvg7fDRC1spqh6yss+bMrriDKNeDQB8Fp15PaNoxZrrA
K12M0IUua/AwlKxcM9AqAxOdE2SoxX9xmhim5xbLh1ctkz0DRy4weZz5ta22A6dQ
vqHKH0uZxtDhAIiw8CqfiIQbBfwFm/xivh170hbVuTqTgoxRpiISB7mgvtuRVHXN
kJgJDrzQ02k8Ah/KjSWxWKaYq88w7lKv9UQPacD8dqNrthZpDAWpQlu5DBB+9Z/0
bW8lxZlU8Ct2/NMxyvArMLa4TFYZnbRFKdc9nBsCAwEAAaNTMFEwHQYDVR0OBBYE
FOjaCjwbTSM6bApDbGmeTh2sZKbjMB8GA1UdIwQYMBaaFOjaCjwbTSM6bApDbGme
Th2sZKbjMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggIBABDDWajB
WWRi9KijQVHgm1EZPsNwZkeCyslHALd1Fh7eLVth3RyFsyZupWM9eI4ZJnY4Rj02
VtR2xSlXioubPt5Ply4IHb/ZCaIRj7WnIFMfwyYxA29O2Yqoi6/Z51Of3qJ1qia7
6ZnDvkf1Ys1pjOVrpvlEL8mYlFYVg+3EC4jy7IljuZ6e24T0HuMoMtelKu7H4SB0
cNOfOeVOD0SZx30YLm32sy7AIXP6BXXuXcM2l3SAtHZgXdQ9eOcrcROLTtdHzVma
8rJxyE51HT6paYOxTVKM7kLT+DipuURTZyIC+Mvmqb0SUPstMuYACuYwICMq35YZ
eXFM2CaU8VkrbaRsDa7OtD2zU/WzHXQn1K5RDd0vw+2IDay3lwTRmJM+/Zp+zxHJ
XGIrQDKm1IXblpD8gq3QkW6YVQZv9FPsXA2GOqomgFji0wEOGu/28KOZoXoASxJw
zCPFMOF/rg0un3U7mBzBQHqYNjSqqBFJQJgPDXpa4P4hCj2GTPHB6PepaXG9nJ4P
17TpNJ3ciwShCVv5u3wAbKVcYhmbOMgEaN4cppHNdzMteOBrQ4k0ZJfO7EBybRjS
h9AOZ2bQDZ0TE/x134WpbNr7gwmmcL6Bl0e87LXHiKu5/6m1mHJG2RhszOl635gW
K/7EvAGSXa2GCL6VSiK0oG6RvKHofBk6snne
-----END CERTIFICATE-----"""

# Save secret by splitting into 2
half_len = int(len(long_secret) / 2)
prt.vault.create_or_update_secret("long_secret_part1", long_secret[:half_len])
prt.vault.create_or_update_secret("long_secret_part2", long_secret[half_len:])

# Load it back
long_secret_part1, age = prt.vault.get_secret("long_secret_part1")
long_secret_part2, age = prt.vault.get_secret("long_secret_part2")
loaded_secret = long_secret_part1 + long_secret_part2

# Confirm they are equal
print("Secrets are equal" if long_secret == loaded_secret else "not equal..")
```
<!-- #endregion -->


---

**Previous**: [Introduction](introduction.md) | **Next**: [Automated Init > Build](automated-init/build.md)
