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

# Caching Large Model and App Files

This example explains how Practicus AI model and hosting handles large model files. Large files, such as GenAI model files, are stored in an object storage system (e.g. in an S3 bucket) and are managed separately from model code (e.g. `model.py`).

We will focus on models, since we usually deal with large files for during model hosting, however, the app hosting system functions similarly.

Upon the first execution of a model, Practicus AI checks the local cache at `/var/practicus/cache/download/files/from/...` for any required large files. If the files are missing or their sizes differ from the remote versions, they are automatically downloaded from the object storage.

## Model Configuration Example

In your `model.json` configuration file, you can specify the folder from which the large files should be downloaded. For example:

```json
{
    "download_files_from": "download/files/from",
    "_comment": "You can also define 'download_files_to'; if not defined, /var/practicus/cache is used as the default target."
}
```

This configuration ensures the model hosting service knows where to look for the large files.

## How It Works

1. **Initial Model Run & Dynamic Downloads:**
   - When a model is executed for the first time (e.g. during development), the system checks the `/var/practicus/cache/download/files/from/...` directory for the required large files.
   - If a file is missing or its size does not match the remote file stored in S3, it is downloaded on the fly.

2. **Pre-baked Files and Production Images:**
   - An admin can build a container image with the large files already pre-loaded in `/var/practicus/cache`. This image is then used for production deployments.
   - In production, when a model is deployed using this image, only smaller model artifacts (like `model.py`) are downloaded if needed because the large files already exist locally.

3. **Incremental Updates:**
   - If only some of the large files have changed between versions, the system downloads only the updated files, reducing the amount of data transferred and speeding up deployments.
     
## Deployment Flexibility

The dual approach provides several benefits:

- **Development and Testing:**
  - Developers work with LLMs as usual. The standard model hosting image downloads large files dynamically from S3 if they are not yet available in `/var/practicus/cache`.

- **Test Deployments:**
  - A model (e.g. `my-model/v3`) is first deployed on a test deployment (e.g. `test-model-deployment`), using the dynamic download approach.

- **Production Deployments:**
  - When ready for production, an admin builds a new container image with the large model files already preloaded to `/var/practicus/cache`.
  - A new production deployment (e.g. `prod-model-deployment-with-large-files`) is created using this image.
  - The admin then updates the model configuration for `my-model/v3` to switch the deployment from the test environment to the production one.

This strategy ensures that production environments start up significantly faster, as they avoid the overhead of downloading large files on every scale-up or recovery.

## Example Scenario

Consider the following end-to-end scenario:

1. **Development Phase:**
   - A developer trains a large language model (LLM) with its associated large files stored in S3.
   - When the model is first used, these large files are automatically downloaded to `/var/practicus/cache` on the deployed container.

2. **Testing Phase:**
   - The developer deploys `my-model/v3` on a test deployment named `test-model-deployment`. In this phase, all large files are downloaded dynamically from S3 as required.

3. **Production Preparation:**
   - When preparing for production, an admin builds a new container image that includes the pre-baked large model files in `/var/practicus/cache`.
   - A new production deployment named `prod-model-deployment-with-large-files` is then created using this updated image.

4. **Production Rollout:**
   - The admin updates the deployment for `my-model/v3` by switching from `test-model-deployment` to `prod-model-deployment-with-large-files`.
   - Practicus AI now `migrates live traffic to the new deployment`. During this transition, the system detects that the large files are already cached locally and skips the download step.

5. **Auto-scaling and Recovery:**
   - If the production deployment `auto-scales` or `recovers after a failure`, new instances spin up with the pre-baked container image, `significantly reducing initialization time` since the large files are already in place.

This scenario maximizes efficiency during both the development phase and in production, ensuring a smooth, scalable, and fast deployment process.

## Summary

- **Large File Downloads:** Files are managed from a centralized object storage system. Initial model runs download any missing or mismatched files into `/var/practicus/cache`.

- **Configuration-Driven:** The download behavior is controlled via `model.json`, enabling customization of cache paths.

- **Flexible Deployments:** Developers can work with dynamic downloads during testing, while production deployments benefit from pre-baked images that drastically reduce startup times, especially during auto-scaling or post-failure recovery.

This approach optimizes both rapid development and efficient production deployments by minimizing redundant downloads and leveraging cached resources.


---

**Previous**: [Work With Data Catalog](work-with-data-catalog.md) | **Next**: [Use Custom Metrics](use-custom-metrics.md)
