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

### Practicus AI Add-ons

Practicus AI Add-ons are external services such as Airflow, MlFlow, observability, analytics etc. that are either installed part of Practicus AI, or embedded as a serice managed by a 3rd party. You can programmatically view, access and view them on your browser.

```python
import practicuscore as prt

# Add-ons are bundled under a Practicus AI region
region = prt.current_region()

# You can also conenct to a remote region instead of the default one
# region = prt.regions.get_region(..)

# Let's make sure you have at least one add-on
if len(region.addon_list) == 0:
    raise NotImplementedError("You do not have any add-ons installed..")
```

```python
# Let's iterate over add-ons
for addon in region.addon_list:
    print("Add-on key:", addon.key)
    print("  Url:", addon.url)
```

```python
# Converting the addon_list into string will give you a csv 
print(region.addon_list)
```

```python
# You can also get add-ons as a pandas DataFrame for convenience
region.addon_list.to_pandas()
```

```python
# Simply accessing the addon_list will print a formatted table string 
region.addon_list
```

```python
first_addon = region.addon_list[0]
# Accessing an add-on object will print it's details
first_addon
```

```python
# You can open the add-on url on an external browser tab
first_addon.open()
```

```python
# If you have the add-on key, you can directly open using region object
addon_key = first_addon.key  # e.g. my-airflow-service
region.open_addon(addon_key)
```

```python
# You can search for an add-on using the region object and add-on key
addon_key = first_addon.key
found_addon = region.get_addon(addon_key)
assert found_addon, f"Addon {addon_key} not found"
found_addon.open()
```


---

**Previous**: [Customizing Templates](customizing-templates.md) | **Next**: [Connections](connections.md)
