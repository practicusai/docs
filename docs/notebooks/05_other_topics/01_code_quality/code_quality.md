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

# Automated Code Quality

You can check for code quality issues, fix and format your files automatically.

```python
import practicuscore as prt

# Let's check for code quality issues in this folder
success = prt.quality.check()
```

```python
# Some issues like 'unused imports' can be fixed automatically
if not success:
    prt.quality.check(fix=True)
```

```python
# Let's also format code to improve quality and readability
prt.quality.format()
```

```python
# Still errors? open bad_code.py and delete the wrong code
# Final check, this should pass
prt.quality.check()
```

```python
# We can add a "No QA" tag to ignore checking a certain type of issue
# E.g. to ignore an unused imports for a line of code
import pandas  # noqa: F401
# To ignore all QA checks (not recommended)
import numpy  # noqa
```

```python

```


## Supplementary Files

### bad_code.py
```python
import pandas 

# this is an error
print(undefined_var)




print("Too many blank lines, which is code formatting issue.")

```


---

**Previous**: [Use Cluster](../../04_distributed_computing/01_spark/03_auto_scaled/02_use_cluster.md) | **Next**: [Sample Notebook](../02_automated_notebooks/sample_notebook.md)