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

### Git source control integration

You can use git commands from the terminal, or with the native Git extension from the Jupyter notebook.


#### Setting up using terminal (recommended)

- Using the main menu open a terminal. File > New > Terminal
- Run the below commands

```shell
# 1) Navigate to the directory to clone 
mkdir ~/projects
cd ~/projects

# 2) Clone a git repo 
git clone https://github.com/username/repository.git

# 3) Enter your username and password
# Note: Many git systems such as GitHub only allow "personal access tokens" as password
# Please check below this notebook to learn how to create a personal access token

# 4) Add your email and username information. 
# This will prevent entering it each time you want to commit.
git config --global user.email "alice@wonderland.com"
git config --global user.name "Alice"

# 5) (Optional) Save your credentials
git config --global credential.helper cache

# If you already cloned a git repo and need to save credentials again
cd ~/projects/name_of_the_repository
git pull
# Enter credentials, and repeat after step 4)
```

After cloning a git repo and saving credentials, you can use both the terminal and the git UI elements inside Jupyter Notebook


#### Setting up using the Jupyter Notebook

- You can open the Git section and click clone a repository.
- Please note that with this method you might have to enter your password each time you want sync with your git repo.



![Setting up from UI](git_setup_ui.png)


#### Creating Git Personal Access Tokens

- Github
    - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- Bitbucket
    - https://support.atlassian.com/bitbucket-cloud/docs/create-a-repository-access-token/
- GitLab
    - https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

```python

```


---

**Previous**: [Test Core Features](../03_automated_tests/test_core_features.md) | **Next**: [Modern Python](../04_virtual_environments/01_modern_python.md)
