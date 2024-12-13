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

### Creating new virtual environments for older Python versions 

Practicus AI workers allow you to create new Python Virtual environments using the python default venv module. If you would liek to use a different Python version, please follow the below steps.

#### Important note
Please note that Prtacticus AI drops support for Python versions that are currently not supported by the Python ecosystem. For this scenartios, you can use Practicus AI workers and notebooks, but not Practicus AI SDK. 


#### Install and initialize conda
- Open Practicus AI juyter notebook, then navigate to: File > New > Terminal
- Run the below
```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda3
rm miniconda.sh

export PATH=$HOME/miniconda3/bin:$PATH
conda init
conda config --set auto_activate_base false
source ~/.bashrc
```


#### Install a specific Python version
- E.g. Python 3.7
```shell
conda create -n py37 python=3.7 -y
conda activate py37
```


#### Add legacy Python to Jupyter

```shell
python3 -m pip install ipykernel
python3 -m ipykernel install --user --name=py37 --display-name "My Legacy Python"
```


#### Install packages

```shell
# Pelase note that you might end up installing an old practicuscore version if your Python version is too old
python3 -m pip install practicuscore
conda deactivate
```


#### Creating new Notebooks

- On Jupyter, click File > New > Notebook.
- And your new virtual environment should show up as an option.

```python

```


---

**Previous**: [Modern Python](modern-python.md) | **Next**: [Dynamic Size Color](../explore-data/01-Plot/Dynamic-Size-Color/Dynamic-Size-Color.md)
