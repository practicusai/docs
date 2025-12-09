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

## Advanced Workspace Configuration

You can specify additional parameters to customize the workspace environment.

```python
import practicuscore as prt

region = prt.get_region()
```

```python
import json
import base64

additional_params = {
    "timezone": "America/Los_Angeles",
    # Setting a custom password is possible, but not recommended.
    "password": "super_secret",
}

additional_params_str = json.dumps(additional_params)
additional_params_b64 = str(base64.b64encode(bytes(additional_params_str, encoding="utf-8")), "utf-8")
```

```python
# Create a workspace with these additional parameters
workspace = region.create_workspace(worker_config={"additional_params": additional_params_b64})
```

```python
username, token = workspace.get_workspace_credentials()

print("Opening Workspace in your browser.")
print(f"Please log in with username: {username} and password: {token}")

login_url = workspace.open_workspace()

# The workspace should now use US Pacific Time, per the timezone setting.
```

```python
workspace.terminate()
```

### Shared Folders

Administrators can define `my` and `shared` folders accessible from your Workspaces. Your `my` folder is dedicated to your environment, while `shared` folders can be used for collaboration with other users.

**Sharing between Workers and Workspaces:** Sometimes, you may have shared folders accessible by both Workspaces and Workers. In such cases, permission issues might arise due to different default users (e.g., practicus vs. ubuntu). To fix this, simply adjust file ownership on the respective environment:

**Fixing file permission issues** of a shared folder:

**On a Workspace**

```
sudo chown practicus:practicus some_file.txt
```

**On a Worker**

```
sudo chown ubuntu:ubuntu some_file.txt
```




---

**Previous**: [Configure Advanced Gpu](configure-advanced-gpu.md) | **Next**: [Create Virtual Envs](create-virtual-envs.md)
