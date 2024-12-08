---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus AI Core
    language: python
    name: practicus
---

<!-- #region editable=true slideshow={"slide_type": ""} -->
# Sample Notebook
This is a sample notebook that you will be executing from another notebook, passing dynamic parameters.

## Defining parameters
- For parameters to work, you must add a tag named "parameters" to any cell, and then define your variables in it.
- To add a tag, please do the below

### Jupyter Lab

Select a cell, move to the upper right on section of Jupyter Lab and click property inspector, and then add a cell tag named "parameters"

![parameters_tag.png](attachment:f7f536a7-2368-437c-8e41-ef2f6b58dc97.png)

### Visual Studio Code

Select a cell, click the ... upper right of the cell and add a cell tag named "parameters"

![parameters_tag2.png](attachment:7a522bec-9224-4bd6-9a2e-b175bba4e99b.png)
<!-- #endregion -->

```python editable=true slideshow={"slide_type": ""}
# Notebook parameters - these can change later
some_param = 1
some_other_param = 2
```

```python editable=true slideshow={"slide_type": ""}
print("Starting to run sample notebook")
```

```python editable=true slideshow={"slide_type": ""}
# This will work now, but will fail later.
if some_param <= 0:
    raise ValueError("some_param must be > 0")
```

```python editable=true slideshow={"slide_type": ""}
print("Finished running sample notebook")
```


---

**Previous**: [Git Integration](../setup_git/git_integration.md) | **Next**: [Run Sample Notebook](run_sample_notebook.md)
