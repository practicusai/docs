---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
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
# To share using VS Code (must run on another worker)
remote_worker = None
# E.g. remote_worker = prt.create_worker(worker_config)

if remote_worker:
    url, token = remote_worker.open_vscode(get_url_only=True)

    print("VS Code login url:", url)
    print("VS Code token    :", token)
```


---

**Previous**: [Personal Startup Scripts](personal-startup-scripts.md) | **Next**: [Upload Files With Apphost](upload-files-with-apphost.md)
