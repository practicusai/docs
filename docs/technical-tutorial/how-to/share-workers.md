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

# Sharing Workers

To allow another user to access a Practicus AI worker you’ve created, you can run the code below and then share the connection details. This provides a quick way to collaborate on the same environment, including data and code.

**Important Note**: Any user you share a worker with will have access to the contents of your `~/my` and `~/shared` directories.

```python
import practicuscore as prt 

# To share the worker you are currently using,
#  first get a reference to 'self'
worker = prt.get_local_worker()

# To start and share a worker, create a worker as usual, e.g.
# worker = prt.create_worker(worker_config)

# The rest of the code will be the same
```

```python
# To share using Jupyter Lab
url = worker.open_notebook(get_url_only=True)

print("Jupyter Lab login url:", url)
```

```python
# To share using VS Code
url, token = worker.open_vscode(get_url_only=True)

print("VS Code login url:", url)
print("VS Code token    :", token)
```


---

**Previous**: [Configure Workspaces](configure-workspaces.md) | **Next**: [View Stats](view-stats.md)
