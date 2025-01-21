---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Access and Refresh JWT tokens

- In this example we will show how to login to a Practicus AI region and get access and or refresh tokens.
- Access tokens are short lived, refresh tokens are long.
- Refresh tokens allow you the ability to store your login credentials without actually storing your password
- JWT tokens are human readable, you can visit jwt.io and view what is inside the token.
    - Is this secure? Yes, jwt.io does not store tokens and decryption happens with javascript on your browser.
    - Who can create JWT tokens? Practicus AI tokens are asymmetric, one can read what is inside a token but cannot create a new one without the secret key. Only your system admin has access to secrets.
    - Can I use a token created for one Practicus AI region for another region? By default, no. If your admin deployed the regions in "federated" mode, yes.

```python
import practicuscore as prt 
import getpass

region = prt.regions.get_default_region()
```

### Defining parameters.
 
This section defines key parameters for the notebook. Parameters control the behavior of the code, making it easy to customize without altering the logic. By centralizing parameters at the start, we ensure better readability, maintainability, and adaptability for different use cases.
 

```python
practicus_url = None # E.g."https://practicus.your-company.com" 
email = None # E.g. "your-email@your-company.com"
password = None
```

```python
assert practicus_url, "Please enter your practicus_url "
assert email, "Please enter your email."
assert password, "Plese enter your password"
```

```python
# Method 1) If you are already logged in, or if you are running this code on a Practicus AI Worker.


# Get tokens for the current region.
refresh_token, access_token = region.get_refresh_and_access_token()

# Will print long strings like eyJ...
print("Refresh token:", refresh_token)
print("Access token:", access_token)
```

```python
# Method 2) You are logging in using the SDK on your laptop,
#   Or, you are running this code on a worker in a region, but logging in to another region.

# Optionally, you can log-out first
# prt.auth.logout(all_regions=True)


# Tip: region.url shows the current Practicus AI service URL that you are logged-in to.



print(f"Please enter the password for {email} to login {practicus_url}")
if not password:
    password = getpass.getpass()

some_practicus_region = prt.auth.login(
    url=practicus_url,
    email=email,
    password=password,
    # Optional parameters:
    # Instead of using a password, you can login using a refresh token or access token
    #   refresh_token = ... will keep logged in for many days
    #   access_token = ... will keep logged in for some minutes
    # By default, your login token is stored for future use under ~/.practicus/core.conf, to disable:
    #   save_config = False
    # By default, your password is not saved under ~/.practicus/core.conf, to enable:
    #   save_password = True
)

# Now you can get as many refresh/access tokens as you need.
refresh_token, access_token = some_practicus_region.get_refresh_and_access_token()

print("Refresh token:", refresh_token)
print("Access token:", access_token)
```

```python
# If you just need an access token.
access_token = region.get_access_token()

print("Access token:", access_token)
```


---

**Previous**: [Integrate Git](integrate-git.md) | **Next**: [Work With Processes](work-with-processes.md)
