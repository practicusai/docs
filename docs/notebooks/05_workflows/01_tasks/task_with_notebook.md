---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

```python
print("This task is running in a notebook")
```

```python
# Code as you would normally do..

import practicuscore as prt

region = prt.get_default_region()

print("Task is running with login credentials of", region.email)
```

```python
print("Let's simulate a failure")

raise SystemError("Simulated error")
```


## Supplementary Files

### task_1.py
```python
print("Hello from simple task 1")
```

### task_2.sh
```bash
echo "Hello from simple task 2"
```

### task_with_error.py
```python
import practicuscore as prt


def main():
    print("Starting task..")

    # Code as usual:
    # - Process data
    # - Train models
    # - Make predictions
    # - Orchestrate other tasks
    # - ...

    try:
        raise NotImplementedError("Still baking..")
    except Exception as ex:
        # Psudo detail log
        with open("my_log.txt", "wt") as f:
            f.write(str(ex))
        raise ex
    
    print("Finished task..")


if __name__ == '__main__':
    main()
```

### task_with_notebook.py
```python
import practicuscore as prt 

print("Starting to run notebook.")

prt.notebooks.execute_notebook(
    "task_with_notebook",
    # By default failed notebooks will not fail caller and just print result.
    # Since this is a task, let's fail the task too.
    raise_on_failure=True,
)

print("Notebook completed running without issues.")

```


---

**Previous**: [Streamlined Model Deployment](../../04_model_building/streamlined_model_deployment/streamlined_model_deployment.md) | **Next**: [Build And Deploy](build_and_deploy.md)
