# Changing VS Code default settings

If you want to customize VS Code each time a worker starts, you can create a file at `~/my/settings/vscode.json`. Any changes you put in this file will **override the default settings**, letting you adjust or add new options without modifying the main configuration. This way, you can keep your own preferences neatly organized and separate from the built-in defaults.

Sample `~/my/settings/vscode.json` settings file that:

- Increases font size
- Ignores certain errors in `ruff` Python Linting

```json
{
    "editor.fontSize": 16,
    "ruff.lint.ignore": [
        "E722", 
        "F401"
    ],
}
```


---

**Previous**: [Cache Large Model Files](cache-large-model-files.md) | **Next**: [Configure Advanced Gpu](configure-advanced-gpu.md)
