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

# Configuring Environment Variables and Secrets at Worker Startup

In this example, we'll show how to pass both standard environment variables and secure secrets from Practicus AI vault (personal and shared) to a Practicus AI Worker. This is especially useful for setting up required configurations during job startup without hardcoding sensitive information.

## Overview
- **Environment Variables:** Set standard OS-level environment variables to be available inside the worker.
- **Personal Secrets:** These secrets are private to you and will be injected as environment variables.
- **Shared Secrets:** These secrets can be shared across projects or team members and also appear as environment variables in the worker.
- **Worker Interaction:** We’ll launch a worker and open a notebook on that worker. Within the worker’s terminal, we can verify that the environment variables and secrets are set correctly (though remember never to log actual secret values in production scenarios!).


```python
import practicuscore as prt

# Configure the worker
worker_config = prt.WorkerConfig(
    worker_size="X-Small",
    env_values={
        "MY_FIRST_ENV": "123",       # Regular environment variable
        "MY_SECOND_ENV": 123          # Another environment variable
    },
    # Personal and shared secrets to be passed as environment variables
    personal_secrets=["MY_PERSONAL_SECRET_1"],
    shared_secrets=["SHARED_SECRET_1"],
)

# Create and start the worker
worker = prt.create_worker(worker_config)

# Open a Jupyter notebook on the new worker
worker.open_notebook()
```

<!-- #region -->
## Verifying Environment Variables and Secrets
Inside the worker’s terminal (not here), you can run:
```bash
echo "MY_FIRST_ENV is: $MY_FIRST_ENV"
echo "MY_SECOND_ENV is: $MY_SECOND_ENV"
# Avoid printing actual secrets in plaintext!
echo "MY_PERSONAL_SECRET_1 length:" $(echo $MY_PERSONAL_SECRET_1 | wc -m)
echo "SHARED_SECRET_1 length:" $(echo $SHARED_SECRET_1 | wc -m)
```

The above commands will help confirm that the environment variables and secrets have been successfully injected into the worker's environment. Note that we never display the actual secret values directly.

<!-- #endregion -->

```python
# Terminate the worker when you're finished.
worker.terminate()
```


---

**Previous**: [Secrets](secrets.md) | **Next**: [Git](git.md)
