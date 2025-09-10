---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Practicus AI Add-ons

Practicus AI Add-ons represent external services integrated into your Practicus AI environment. These can include 

- **Airflow** for workflows
- **MLflow** for experiment tracking
- **Observability tools**
- **Analytics Services**
- and more..

In addition to Practicus AI Home and AI Sudio, you can also view them, and open their interfaces directly from the SDK.

```python
import practicuscore as prt

# Add-ons are tied to a Practicus AI region
region = prt.current_region()

# Ensure that add-ons are available
if len(region.addon_list) == 0:
    raise NotImplementedError("No add-ons installed.")
```

```python
# Iterate over available add-ons
for addon in region.addon_list:
    print("Add-on key:", addon.key)
    print("  URL:", addon.url)
```

```python
# Printing addon_list directly returns a CSV-like formatted text
print(region.addon_list)
```

```python
# Convert addon_list to a pandas DataFrame for convenience
region.addon_list.to_pandas()
```

```python
first_addon = region.addon_list[0]
# Accessing an add-on object prints its details
first_addon
```

```python
# Open the add-on in your default browser
first_addon.open()
```

```python
# If you know the add-on key, you can open it directly from the region
addon_key = first_addon.key
region.open_addon(addon_key)
```

```python
# Search for a specific add-on by key
addon_key = first_addon.key
found_addon = region.get_addon(addon_key)
assert found_addon, f"Addon {addon_key} not found"
found_addon.open()
```


---

**Previous**: [Workspaces](workspaces.md) | **Next**: [Modeling > Introduction](../modeling/introduction.md)
