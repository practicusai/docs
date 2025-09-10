---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# Practicus AI Model Hosting Foundations

Practicus AI provides a robust model deployment infrastructure that allows you to organize, host, and manage machine learning models with scalability, security, and flexibility.

## Model Prefixes

Models in Practicus AI are **logically grouped** using model prefixes. A model prefix serves as a namespace, often reflecting organizational or access boundaries. For example:

```
https://practicus.company.com/models/marketing/churn/v6/
```

In this URL:

- `models/marketing` is the model prefix
- `churn` is the model name
- `v6` is an optional version

These prefixes can also be tied to security and access controls, ensuring that only authorized user groups (e.g., an LDAP group for finance) can access certain prefixes and the models under them.

## Model Deployments

While model prefixes handle logical grouping and naming, model deployments represent the **physical Kubernetes deployments** that host these models. Model deployments:

- Run on Kubernetes
- Can host multiple models and model versions
- Part of an integrated service mesh and load balancing
- Support advanced techniques like A/B testing between model versions
- Can be auto-scaled

This architecture enables flexible model hosting where **you can deploy multiple versions of a model under the same prefix but on different deployments**, ensuring isolation, performance optimization, and continuous integration and delivery of models.

You can use the Practicus AI App, CLI, or this SDK to list, navigate, and interact with model prefixes, deployments, models, and their versions.

```python
import practicuscore as prt

# Connect to the current region
region = prt.current_region()
```

```python
# List the model prefixes defined by your admin and accessible to you
region.model_prefix_list.to_pandas()
```

```python
# List the model deployments defined by your admin and accessible to you
region.model_deployment_list.to_pandas()
```

### Re-creating a Model Deployment

If you have admin privileges, you can re-create a model deployment. Re-creating involves deleting and then re-launching the deployment using the existing configuration. This is **helpful in development or testing scenarios to ensure a fresh start.** However, it’s not typically advised in production environments since model versions hosted by that deployment will be temporarily unavailable during the process.

**Note:** You must have admin privileges for this operation.

```python
model_deployment_key = "development-model-deployment"
region.recreate_model_deployment(model_deployment_key)
```


---

**Previous**: [Add-Ons](../getting-started/add-ons.md) | **Next**: [Sample Modeling > Build And Deploy](sample-modeling/build-and-deploy.md)
