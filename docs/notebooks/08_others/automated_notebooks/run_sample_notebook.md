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
# Automated tests using notebooks

Practicus AI allows you to execute notebooks in autoamted fashion, which can be used for various purposes including testing.
<!-- #endregion -->

```python
import practicuscore as prt
```

```python editable=true slideshow={"slide_type": ""}
# This will run just fine, and save the resulting output 
prt.notebooks.execute_notebook("sample_notebook")
```

```python editable=true slideshow={"slide_type": ""}
# This will FAIL since some_param cannot be 0
prt.notebooks.execute_notebook(
    "sample_notebook",
    parameters={
        "some_param": 0 
    }
)
```

<!-- #region editable=true slideshow={"slide_type": ""} -->
## Advanced features
<!-- #endregion -->

```python editable=true slideshow={"slide_type": ""} tags=["parameters"]
# Advanced Notebook automation parameters
default_output_folder="~/tests"  # If none, writes notebook output to same folder as notebook
default_failed_output_folder="~/tests_failed"  # If not none, collects failed notebook results 
```

```python editable=true slideshow={"slide_type": ""}
# By calling configure you can save notebook results to central location
# Please note that you can do this to a shared/ folder daily where all of our members have access to
prt.notebooks.configure(
    default_output_folder=default_output_folder,
    default_failed_output_folder=default_failed_output_folder,
    add_time_stamp_to_output=True,
)
```

```python editable=true slideshow={"slide_type": ""}
# This will work
prt.notebooks.execute_notebook("sample_notebook")
```

```python editable=true slideshow={"slide_type": ""}
# This will fail but does not stop the execution of the notebook
prt.notebooks.execute_notebook(
    "sample_notebook",
    parameters={
        "some_param": 0 
    }
)
```

```python editable=true slideshow={"slide_type": ""}
# Calling validate_history() will raise an exception IF any of the previous notebooks failed
# This is useful to have a primary "orchestration" notebook that executes other child notebooks,
# And then finally fails itself if there was a mistake. 
# You can then report the result, essentially creating a final report. 
prt.notebooks.validate_history()

# You can view the passed and failed execution results in 
# ~/tests and ~/tests_failed with a time stamp (optional)
```

 ### Executing notebooks from terminal
 
You can run the below command to execute a notebook from the terminal or an .sh script.

```shell
prtcli execute-notebook -p notebook=my-notebook.ipynb 
```  
