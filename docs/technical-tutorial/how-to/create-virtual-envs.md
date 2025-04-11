---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Creating new virtual environments 

Practicus AI workers allow you to create new Python Virtual environments using the python default venv module. Please follow the below steps to create and use new virtual environments.

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
# Install packages, these will 'override' parent python package versions
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

## Creating New Virtual Environments for Older Python Versions Using `uv`

If you need to use a Python version older than the one provided by default, you can leverage `uv` to install that version and then use Python’s built-in `venv` module to create and manage your virtual environments.

#### Important Note
Practicus AI may not fully support older, deprecated Python versions. While you can still run these versions in a Practicus AI worker or notebook, certain features (like the Practicus AI SDK) may not function as expected.

#### Installing a Specific Python Version
Since `uv` is already installed, you can use it to install an alternate Python version. For example, to install Python 3.7:

```shell
uv python install 3.7
```

#### Creating a Virtual Environment
Use the newly installed Python version to create a virtual environment:

```shell
uv venv ~/.venv/test --python 3.7
```

Activate the virtual environment:

```shell
source ~/.venv/test/bin/activate
```

#### Installing Packages
Within the activated environment, install your desired packages:

```shell
uv pip install pandas
```


---

**Previous**: [Startup Scripts](startup-scripts.md) | **Next**: [Model Tokens](model-tokens.md)
