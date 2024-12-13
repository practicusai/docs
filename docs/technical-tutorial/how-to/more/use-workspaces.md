---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

###  Practicus AI Workspaces 

Practicus AI Workspaces is a web based remote desktop environment with Practicus AI Studio and many other tools pre-installed and pre-configured. 

![workspaces.png](attachment:9d691f5e-127c-455e-bba2-b18e6f2109c6.png)

They live in a Practicus AI region and you can create, work with and terminate them with he below commands.


#### Simple use of Workspaces

```python
import practicuscore as prt

# Workers are created under a Practicus AI region
region = prt.current_region()

# You can also connect to a remote region instead of the default one
# region = prt.get_region(..)
```

```python
# Let's view our region
region
```

```python
# The below is the easiest way to start working with a worker 
workspace = region.create_workspace()
```

```python
# Let's view workspace details
workspace
```

```python
# A Workspace is actually a "worker" too, so you can list all workers and workspaces with the same command
# Please note the "service_type" column
region.worker_list.to_pandas()

# To use an existing wokspace
# workspace = region.worker_list[0]
```

```python
# Lets get the login credentials for our newly created workspace
username, token = workspace.get_workspace_credentials()

print("Opening Workspace in your browser")
print(f"Pelase login with username: {username} and password: {token}")

login_url = workspace.open_workspace()

# You can only get the URL wihtout opening in your browser with get_url_only=True
# login_url = workspace.open_workspace(get_url_only=True)
```

```python
# You can terminate a workspace using the below command
workspace.terminate()
```

```python
# If you terminate all of your workers in a region, you will also terminate all your workspaces
# region.terminate_all_workers()
```

### Shared folders

Ideally, an admin will define "my" and "shared" folders for your Workspaces.

Your "my" folder will be shared between all of your workspaces, and the shared folders between select users and their workspaces allowing better collaboration.

#### Sharing folders between Workers and Workspaces   
  
An admin can also define shared folders that are accessible by both Workspaces and Workers. In this case, please be careful about potential write permission issues.

E.g. You can write a file from Workspace (practicus user with id 911) and you won't be able to overwrite that file from a Worker (ubuntu user with id 1000) without changing permissions first. To resolve this unique issue:

On a Workspace, to change ownership of a file you can run:
```
sudo chown practicus:practicus some_file.txt
```

On a Worker, to change ownership of a file you can run:
```
sudo chown ubuntu:ubuntu some_file.txt
```



### Advanced Usage

```python
# You can provide additional parameters for workspace creation
import json 
import base64 

additional_params = {
    # If you don't select a timezone, UTC (Greenwich Mean Time) default will be used
    "timezone": "America/Los_Angeles",
    # You can also select custom password. This is ** not recommended ** due to weak security.
    "password": "super_secret",
}

# Additional params need to be base64 encoded
additional_params_str = json.dumps(additional_params)
additional_params_b64 = str(base64.b64encode(bytes(additional_params_str, encoding="utf-8")), "utf-8")
```

```python
# Create a new workspace with additional_params
workspace = region.create_workspace(
    worker_config = {
        "additional_params": additional_params_b64
    }
)
```

```python
username, token = workspace.get_workspace_credentials()

print("Opening Workspace in your browser")
print(f"Pelase login with username: {username} and password: {token}")

login_url = workspace.open_workspace()

# You should now see that the computer clock is using US Pacific time zone 
```

```python
workspace.terminate()
```


---

**Previous**: [Use Workers](use-workers.md) | **Next**: [Use Addons](use-addons.md)
