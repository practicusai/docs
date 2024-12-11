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

###  Practicus AI Worker Notebooks

You can start a Practicus AI worker and open Jupyter Notebook using the App, SDK or CLI.

```python
import practicuscore as prt 

worker_config = {
    "worker_size": "X-Small",
    "worker_image": "practicus",
}
worker = prt.create_worker(worker_config)
```

```python
# Open the Jupyter notebook on a new browser tab
print(f"Opening jupyter notebook of {worker.name}")
notebook_login_url = worker.open_notebook()
```

```python
# You can change the UI theme color to light
# Note: this will only work the first time you open the notebook on a given worker
notebook_login_url = worker.open_notebook(dark_mode=False)
```

```python
# You can get the login url and skip opening the notebook in a new browser tab
notebook_login_url = worker.open_notebook(get_url_only=True)
print(notebook_login_url)
```

```python
worker.terminate()
```


---

**Previous**: [Open Vscode](open-vscode.md) | **Next**: [Workers](workers.md)
