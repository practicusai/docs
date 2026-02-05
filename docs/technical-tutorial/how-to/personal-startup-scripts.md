---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

<!-- #region -->
# Personal Startup Scripts

This expample demonstrates how personal startup scripts for Practicus AI workers are executed.

## Startup Script Execution Order

1. **Static Startup Script:**
   - If a user creates the file `~/my/scripts/startup.sh`, it is automatically executed on startup by all workers.
   - To test, create `~/my/scripts/startup.sh` and save the below example script to personalize VS Code on startup.
     
```bash
#!/bin/bash

echo "Updating VS Code settings to always use dark mode."
echo '{"workbench.colorTheme": "Default Dark Modern"}' > "/home/ubuntu/.local/share/code-server/User/settings.json"
```

**Note:** If your script requires network access, add retries with sleep commands. Networking services may not be 
immediately available during worker startup.

2. **Dynamic Startup Script:**
   - If the user provides an additional dynamic startup script (via the worker configuration), the static script is executed first, followed by the dynamic startup script.

```python
import practicuscore as prt

worker_config = prt.WorkerConfig(
    worker_image="practicus",
    worker_size="Medium",
    startup_script="""
    
    echo "Executing dynamic startup script, will only run on the selected worker."
    
    """
)

worker = prt.create_worker(worker_config)
```

3. **Error Logging:**
   - If there are errors in any of the scripts, detailed error information can be viewed in the file `~/script.log`.


## Summary

In summary:

- **Static Script:** Located at `~/my/scripts/startup.sh`, it is always executed first on worker startup.
  
- **Dynamic Script:** Provided in the worker configuration (as seen above), it runs after the static script.
  
- **Error Handling:** Any errors during the execution of either script will be recorded in `~/script.log`.
<!-- #endregion -->


---

**Previous**: [Model Tokens](model-tokens.md) | **Next**: [Share Workers](share-workers.md)
