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

<!-- #region editable=true slideshow={"slide_type": ""} -->
# Testing Core Features

This notebook utilizes other notebooks on the worker to demonstrate their usage, and allows automated testing.
<!-- #endregion -->

```python editable=true slideshow={"slide_type": ""} tags=["parameters"]
# Notebook parameters
some_param = None

# Where to write test results
default_output_folder="~/tests"
default_failed_output_folder="~/tests_failed"
```

```python editable=true slideshow={"slide_type": ""}
# Validate key parameters are set
# e.g. assert some_param
```

```python editable=true slideshow={"slide_type": ""}
import practicuscore as prt

prt.notebooks.configure(
    default_output_folder=default_output_folder,
    default_failed_output_folder=default_failed_output_folder,
)
```

```python editable=true slideshow={"slide_type": ""}
prt.notebooks.execute_notebook(
    "~/samples/notebooks/01_getting_started/01_insurance.ipynb",
)
```

```python editable=true slideshow={"slide_type": ""}
# Add other notebook tests here
```

```python
# Fail this notebook by raising an Exception
#   if ANY of the prior notebook executions failed.
prt.notebooks.validate_history()
```


---

**Previous**: [Executing Notebooks](../automate-notebooks/executing-notebooks.md) | **Next**: [Git Integration](../configure-git/git-integration.md)
