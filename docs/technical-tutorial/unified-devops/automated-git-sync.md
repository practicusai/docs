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

# Automated Git Sync for Workers

This example demonstrates how to securely configure Git in Practicus AI, ensuring you can clone or pull a repository both locally (within a running notebook) and automatically when a worker starts.

## Overview
1. **Create a Personal Access Token (PAT)** on your chosen Git platform.
2. **Store the PAT as a Personal Secret** in the Practicus AI Vault.
3. **Configure and Sync the Repository** via the Practicus AI Git Helper.
4. **Auto-Clone a Repo on Worker Startup** to have your code ready immediately when the worker launches.



### Step 1: Create a Personal Access Token
Log into your Git system (e.g., Practicus AI Git, GitHub, GitLab, ..) and generate a personal access token.
Make sure to include any necessary permissions (e.g., read/write to repositories if needed).


### Step 2: Store the Token as a Personal Secret
Store the new token in the Practicus AI Vault to keep it secure and avoid hardcoding credentials in your code.

```python
worker_size = None
```

```python
assert worker_size, "Please enter your worker_size."
```

```python
import practicuscore as prt
from getpass import getpass

# Define a name for the stored secret
git_secret_name = "MY_GIT_SECRET"

# Prompt for your personal access token
key = getpass("Enter your Git personal access token:")

# Store or update the token in the Practicus AI Vault
prt.vault.create_or_update_secret(name=git_secret_name, key=key)
print(f"Successfully saved secret '{git_secret_name}' in Practicus AI Vault.")
```

### Step 3: Configure Git and Synchronize the Repository
Specify details such as the repository URL, which secret to use, and optional parameters like branch name, fetch depth, or sparse checkout folders.


```python
import os

remote_url = "https://git.practicus.my-company.com/myuser/myrepo.git"  # Example repository URL

# Create a GitConfig object
git_config = prt.GitConfig(
    remote_url=remote_url,  # Repository to clone or pull
    secret_name=git_secret_name,  # Name of the secret containing the PAT
    # Optional configurations:
    # username="your-username",  # If the Git username differs from your Practicus AI username
    # save_secret=True,
    # local_path="~/some-path-on-worker",
    # branch="main",
    # sparse_checkout_folders=["folder1", "folder2"],
    # fetch_depth=1,
)

# For demonstration, retrieve the token in this local notebook (avoid printing it!)
os.environ[git_secret_name], age = prt.vault.get_secret(git_secret_name)
print(f"Retrieved secret '{git_secret_name}', and it is {age} days old.")

# Sync the repository locally in this current environment
prt.git.sync_repo(git_config)
print("Repository synced locally.")
```

### Step 4: Auto-Clone or Pull the Repo on Worker Startup
Using `git_configs` in the `WorkerConfig`, you can automatically clone or pull the repository when the worker is created. This ensures your environment has the code ready immediately.


```python
# Configure a new worker to automatically clone your repository
worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    personal_secrets=[git_secret_name],
    git_configs=[git_config],
)

# Create and start the worker
worker = prt.create_worker(worker_config)

# Open a notebook on the new worker
worker.open_notebook()
```

## Cleanup
Terminate the worker when you are finished.

```python
worker.terminate()
```

## Git Configuration via the Web UI

You can also manage your Git settings and secrets through Practicus Home's web interface. To get started:

1. **Access Your Home Page:**
   Navigate to your home page (e.g., https://practicus.my-company.com).

2. **Manage Your Secrets:**
   Open the **Settings** menu, then select **Create Secret** to add or update existing secrets.

3. **Configure a New Worker:**
   When creating a new worker, select **Advanced Settings** and choose the desired Git configuration and apply the secrets you just saved.

This streamlined process makes it simple to securely set up your Git configuration without leaving the web UI. Enjoy seamless integration with Practicus Home!


---

**Previous**: [Build](automated-init/build.md) | **Next**: [Git Integrated CICD](git-integrated-cicd.md)
