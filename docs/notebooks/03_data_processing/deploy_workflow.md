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

```python
import practicuscore as prt

service_key = "airflow-dev"
dag_key = "california"
files_path = "/home/ubuntu/practicus/generated/california" 
# workflow_files_dir_path = None  # None for current directory

prt.workflows.deploy(
    service_key=service_key, 
    dag_key=dag_key, 
    files_path=files_path
)
```
