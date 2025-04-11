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

# Practicus AI Startup Scripts

This notebook explains how startup scripts for Practicus AI workers are executed.

<!-- #region -->
## Startup Script Execution Order

1. **Static Startup Script:**
   - If a user creates the file `~/my/scripts/startup.sh`, it is automatically executed on startup by all workers.
   - To test, create `~/my/scripts/startup.sh` and save the below
     
```bash
#!/bin/bash

echo "Executing shared startup script in ~/my folder."
echo "Changing VS Code Settings, so it's always in dark mode."
echo '{"workbench.colorTheme": "Default Dark Modern"}' > "/home/ubuntu/.local/share/code-server/User/settings.json"
echo "All of my workers will run this script in startup."
```

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

**Previous**: [View Stats](view-stats.md) | **Next**: [Create Virtual Envs](create-virtual-envs.md)
