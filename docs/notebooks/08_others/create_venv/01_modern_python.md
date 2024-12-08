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

### Creating new virtual environments 

Practicus AI workers allow you to create new Python Virtual environments using the python default venv module. Pelase follow the below steps to create and use new virtual environments.


#### Option 1) Re-use base python packages
- With this option you can save disk space with fewer package installations 
- If you need to change a python package version of base image you can simply pip install the different version.
  
```shell
# Create new venv 
python3 -m venv $HOME/.venv/new_venv --system-site-packages --symlinks
# Activate
source $HOME/.venv/new_venv/bin/activate
# Add to Jupyter 
python3 -m ipykernel install --user --name new_venv --display-name "My new Python"
# Install packages, these will 'overide' parent python package versions
python3 -m pip install some_package
```


#### Option 2) Fresh install
- With the fresh install you will have to install all packages, including Practicus AI
  
```shell
# Create new venv 
python3 -m venv $HOME/.venv/new_venv
# Activate
source $HOME/.venv/new_venv/bin/activate
# Install Jupyter Kernel
python3 -m pip install ipykernel
# Add to Jupyter 
python3 -m ipykernel install --user --name new_venv --display-name "My new Python"
# Install packages
python3 -m pip install practicuscore
```


#### Creating new Notebooks

On Jupyter click File > New > Notebook. And your new virtual environment should show up.

```python

```


---

**Previous**: [Code Quality](../code_quality/code_quality.md) | **Next**: [Legacy Python](02_legacy_python.md)
