---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

## Practicus AI Model Foundation

Below you can read about a simplified version of the Practicus AI model hosting foundation. 

### Model Prefixes

Practicus AI models are **logically** grouped with the model prefix concept using the https:// [some.address.com] / [some/model/prefix] / [model-name] / [optional-version] / format. E.g. https://practicus.company.com/models/marketing/churn/v6/ can be a model API address where _models/marketing_ is the prefix, _churn_ is the model, and _v6_ is the optional version.

### Model Deployments

Models are **physically** deployed to Kubernetes, featuring characteristics such as capacity, auto-scaling, and enhanced security.

You can use the Practicus AI App, the SDK or CLI to navigate model prefixes, deployments, models and model versions.

```python
import practicuscore as prt

# Add-ons are bundled under a Practicus AI region
region = prt.current_region()

# You can also conenct to a remote region instead of the default one
# region = prt.regions.get_region(..)
```

```python
# Let's list the model prefixes that the admin defined 
#   AND I have access to
region.model_prefix_list.to_pandas()
```

```python
# Let's list the model deployments that the admin defined 
#   AND I have access to
region.model_deployment_list.to_pandas()
```

#### Re-creating a model deployment

- You can re-create (first delete, and then create) a model deployment using existing model deployment configuration.
- This can be a useful operation during dev/test, but not a very ideal operation in a production setting since all models on this model deployment will not be available while their host is being re-created.
- **You must have admin privileges on the model deployment to perform this operation.**

```python
model_deployment_key = "development-model-deployment"
region.recreate_model_deployment(model_deployment_key)
```


---

**Previous**: [Workers](workers.md) | **Next**: [Data Catalog](data-catalog.md)
