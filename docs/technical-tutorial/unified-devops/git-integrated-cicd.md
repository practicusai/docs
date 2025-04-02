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

# Git-Integrated CI/CD

Practicus AI offers CI/CD runners that are **compatible with GitHub Actions** workflows. These runners let you integrate code pushes, tests, and automated tasks seamlessly with Practicus AI’s infrastructure—even in **air-gapped** or private deployments.

## Overview
1. **Add a Workflow Configuration:** Create a `.github/workflows/` directory in your repository and add a YAML configuration to define your workflows.
2. **Specify a Runner:** Use `runs-on: practicus-XX.X.X` to leverage Practicus AI runners.
3. **Add Secrets:** Store Practicus AI credentials (like a refresh token) or other required secrets in your Git repository settings.
4. **Create CI/CD Task Scripts:** Use Python scripts (or the Practicus AI CLI) to launch tasks (like spinning up workers or building containers) on Practicus AI.

Below are some examples of how to set up and run these workflows.



## Basic Workflow Example
Create a workflow file (for example, `test.yaml`) inside `.github/workflows/` in your repository:

```yaml
# .github/workflows/test.yaml
name: Test CICD actions

on:
  - push

jobs:
  Sample-Job:
    runs-on: practicus-24.8.4
    steps:
      - name: Say Hello
        run: echo "Hello"
```

Whenever you push code, this workflow will run on the Practicus AI runner. You can view logs and status on the repository’s **Actions** page.



## Using Practicus AI in a Workflow
You can trigger Practicus AI workers, tasks, or container builds directly in your workflow. Let’s walk through an example.



### Step 1: Obtain a Practicus AI Refresh Token
In Practicus AI, generate a refresh token for your account, then store it privately.


```python
worker_size = None
startup_script = """echo "Hello from Practicus AI unified DevOps""""
```

```python
assert worker_size, "Please enter your worker_size."
assert startup_script, "Please enter your startup_script."
```

```python
import practicuscore as prt

# Retrieve your personal refresh token
refresh_token = prt.auth.get_refresh_token()
print("Your refresh token is:", refresh_token)
print("Keep this token private and clear the cell/terminal output immediately!")
```

### Step 2: Save the Token as a Repository Secret
Go to your Git repository settings (e.g., Settings > Secrets > Actions on GitHub) and add a new secret named `PRT_TOKEN`. Paste the refresh token you obtained above.

> **Note:** Do not store a short-lived access token. It will expire quickly, causing your CI/CD workflows to fail. Use the refresh token instead.


### Step 3: Create a Task File in the Repository
Below is a simple Python script (`cicd/start_worker.py`) that spins up a Practicus AI worker, runs a command, and terminates it.

```python
# cicd/start_worker.py
import practicuscore as prt

worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    startup_script=startup_script
)

print("Starting worker...")
worker = prt.create_worker(worker_config)

print("Terminating worker...")
worker.terminate()
```

### Step 4: Reference the Task File in Your Workflow
Add a workflow file (e.g., `.github/workflows/using_workers.yaml`) that sets the appropriate environment variables and runs your script.

```yaml
# .github/workflows/using_workers.yaml
name: Using Practicus AI Workers

# This action will run each time code is pushed to the repository
on:
  - push

env:
  # Update with your Practicus AI URL
  PRT_URL: https://practicus.my-company.com
  PRT_TOKEN: ${{ secrets.PRT_TOKEN }}

jobs:
  Explore-PracticusAI-Actions:
    runs-on: practicus-24.8.4
    steps:
      - uses: actions/checkout@v4

      - name: Perform some task on a Practicus AI Worker
        run: python cicd/start_worker.py

      - name: View Practicus AI CLI help
        run: prtcli --help
```
After saving and pushing these changes, the Practicus AI runner will automatically execute your workflow.



## More Complex Task Examples

### Example 1: Upload and Execute a Task File
Use `prt.run_task(...)` to start a worker, upload specified files, and run them automatically. This requires that all the files your task depends on are in the directory you provide.


```python
# cicd/task.py
print("Hello from a simple task")
```

```python
# cicd/run_task.py
import practicuscore as prt

worker_config = prt.WorkerConfig(
    worker_size=worker_size,
)

task_file = "task.py"  # The file to run

print(f"Starting {task_file} on a new worker.")
worker, success = prt.run_task(
    file_name=task_file,
    files_path="cicd",       # Local folder containing task.py
    worker_config=worker_config,
)

if success:
    print("Task execution finished successfully.")
else:
    raise SystemError(f"{task_file} failed.")
```

You can tie this script to a workflow file, for example:

```yaml
# .github/workflows/run_task.yaml
name: Run a task on Practicus AI Worker

# This action will run each time code is pushed to the repository
on:
  - push

env:
  # Update the below url
  PRT_URL: https://practicus.my-company.com
  PRT_TOKEN: ${{ secrets.PRT_TOKEN }}

jobs:
  Explore-PracticusAI-Actions:
    runs-on: practicus-24.8.4
    steps:
      - uses: actions/checkout@v4

      - name: Run task.py on a Practicus AI Worker
        run: python cicd/run_task.py
```



### Example 2: Use Git Instead of Uploading Files
If your code exists in a Git repository, you can clone or pull the repo on the worker automatically and then execute a file directly from the cloned repo. First, ensure you have a Git personal access token saved in the Practicus AI Vault.

```python
import practicuscore as prt
from getpass import getpass

personal_secret_name = "MY_GIT_SECRET"
key = getpass(f"Enter key for {personal_secret_name}:")

prt.vault.create_or_update_secret(name=personal_secret_name, key=key)
print(f"Git access token saved as secret '{personal_secret_name}'.")
```

```python
# cicd/run_from_git_repo.py
import practicuscore as prt

remote_git_url = "http://git.practicus.my-company.com/myuser/myproject"
git_secret_name = "MY_GIT_SECRET"
local_path_for_git = "~/myproject"

# Configure the Git repository and secret
git_config = prt.GitConfig(
    remote_url=remote_git_url,
    secret_name=git_secret_name,
    local_path=local_path_for_git,
)

# Create a WorkerConfig that auto-clones the repo
worker_config = prt.WorkerConfig(
    worker_size=worker_size,
    personal_secrets=[git_secret_name],
    git_configs=[git_config],
)

# Path to the script we want to run inside the worker, will be cloned from Git.
task_file_on_worker = f"{local_path_for_git}/cicd/task.py"

print(f"Starting {task_file_on_worker} on a new worker.")
worker, success = prt.run_task(
    upload_files=False,              # We'll rely on Git instead of uploading files
    file_path_on_worker=task_file_on_worker,
    worker_config=worker_config,
)

if success:
    print("Task finished successfully.")
else:
    raise SystemError(f"{task_file_on_worker} failed.")
```

And reference it in a workflow file, for example:

```yaml
# .github/workflows/run_from_git_repo.yaml
name: Running tasks from Git Repo

# This action will run each time code is pushed to the repository
on:
  - push

env:
  # Update the below url
  PRT_URL: https://practicus.my-company.com
  PRT_TOKEN: ${{ secrets.PRT_TOKEN }}

jobs:
  Explore-PracticusAI-Actions:
    runs-on: practicus-24.8.4
    steps:
      - uses: actions/checkout@v4

      - name: Run a file from Git on a Practicus AI Worker
        run: python cicd/run_from_git_repo.py
```


## Conclusion
By combining Practicus AI’s worker orchestration with your Git repository’s CI/CD configuration, you can automate virtually any workflow—ranging from running tests and building containers to complex data processing jobs. Just push your changes, and Practicus AI takes care of the rest.

You can track the status of each workflow run in your repository’s “Actions” tab (or equivalent, depending on your Git service).


---

**Previous**: [Automated Git Sync](automated-git-sync.md) | **Next**: [Build Custom Images](build-custom-images.md)
