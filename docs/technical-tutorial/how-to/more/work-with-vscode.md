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

###  Practicus AI Worker Visual Studio Code

You can start a Practicus AI worker and open VS Code using the App, SDK or CLI.

```python
import practicuscore as prt 

worker_config = {
    "worker_size": "X-Small",
    "worker_image": "practicus",
}
worker = prt.create_worker(worker_config)
```

```python
# Open VS Code on a new browser tab
print(f"Opening VS Code of {worker.name}")
vscode_login_url, vscode_password = worker.open_vscode()
print("Password:", vscode_password)
```

```python
# You can change the UI theme color to light
# Note: this will only work the first time you open VS Code on a given worker
vscode_login_url, vscode_password = worker.open_vscode(dark_mode=False)
print("Password:", vscode_password)
```

```python
# You can get the login url and skip opening VS Code in a new browser tab
vscode_login_url, vscode_password = worker.open_vscode(get_url_only=True)
print(vscode_login_url, "Password:", vscode_password)
```

```python
worker.terminate()
```


---

**Previous**: [Work With Notebooks](work-with-notebooks.md) | **Next**: [Work With Processes](work-with-processes.md)
