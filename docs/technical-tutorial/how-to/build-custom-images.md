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

# Building and using custom container images

In this example, we'll demonstrate how to build custom container images using the Practicus AI platform. You’ll see how to:

1. **Start a Worker** with container-building capabilities.
2. **Create and push a custom container image** to a private registry.
3. **Use your custom container** to run new Practicus AI Workers.

Along the way, we’ll discuss:

- Configuring the builder to allocate a percentage of your Worker’s resources.
- Pushing images to Practicus AI container registry or other container registries.
- Granting security permissions to allow custom images.

We’ll also cover **advanced topics** like privileged builds, custom builder images, and separating credentials for pulling and pushing.


## Step 1: Start a Worker with Image-Building Capabilities

First, we'll create a Practicus AI Worker that can build container images. This Worker uses two containers:

1. **Primary Container (Ubuntu Linux):** Contains your main environment.
2. **Builder Container (Alpine Linux):** Builds container images under the hood.

The primary container orchestrates the builder. By setting `builder=True` in `ImageConfig`, you're opting to start this secondary container and optionally specify how much of your Worker’s resources it can use.

```python
import practicuscore as prt

# Configure a Worker that can build container images.
image_config = prt.ImageConfig(
    builder=True,  # Enables the builder container.
    builder_capacity=60,  # Optional: allocates 60% of CPU/RAM/GPU to the builder.
    insecure_registries="my-registry.practicus.my-company.com",  # Optional: use HTTP instead of HTTPS
)

worker_config = prt.WorkerConfig(
    worker_image="practicus-minimal",
    worker_size="Small-restricted",
    image_config=image_config,
)

# Create and open the new Worker.
builder_worker = prt.create_worker(worker_config)
builder_worker.open_notebook()
```

## Step 2: Build and Push Your Custom Image

Within the `builder_worker` notebook, you'll have access to the `~/build` directory—shared by the primary container and the builder container. Follow these steps to build your image:

1. Add files (e.g., application code, Dockerfile, config files) to `~/build`.
2. Run `build_image` with any necessary credentials.
3. Optionally push the image to your registry.

Let's create a small text file and a simple Dockerfile, then build and push.

```python
# Create a text file in ~/build
with open("/home/ubuntu/build/hello.txt", "wt") as f:
    f.write("Hello from the custom container image!")
```

```python
# Create a Dockerfile in ~/build
dockerfile_content = """
# Use a base image from your private registry or a public source
FROM my-registry.practicus.my-company.com/practicusai/practicus-minimal:24.8.3

# Copy in our text file
COPY hello.txt /home/ubuntu/hello.txt

# (Optional) Install packages via apt or pip if needed.
# RUN sudo apt-get update && sudo apt-get install -y <packages>
# RUN pip install <libraries>
"""

with open("/home/ubuntu/build/Dockerfile", "wt") as f:
    f.write(dockerfile_content)
```

```python
# Build and push the image
repo_username = "some-user-name"
repo_password = "some-token"

success = prt.containers.build_image(
    name="my-registry.practicus.my-company.com/demo/practicus-minimal-my",
    tag="24.8.3",
    push_image=True,
    registry_credentials=[
        ("my-registry.practicus.my-company.com", repo_username, repo_password),
    ],
    insecure_registry=True,
)

print("Successful!" if success else "Failed..")
```

Once your image is successfully pushed, you can reference it in any future Practicus AI Worker by its full name, e.g., `my-registry.practicus.my-company.com/demo/practicus-minimal-my:24.8.3`.


## Step 3: Use the Custom Image

Switch back to your original environment (the one where you created `builder_worker`). Now you can create a new Worker that runs on your freshly built image. Make sure your user or user group has permissions to use custom container images. If you’re an admin, you can grant this permission in the Practicus AI admin console under **Infrastructure** > **Container Images**.

Below is an example of how to run a Worker with the custom image:


```python
import practicuscore as prt

image_config = prt.ImageConfig(
    repo_username="some-user-name",
    repo_password="some-token"
)

worker_config = prt.WorkerConfig(
    # If desired, specify a tag explicitly, 
    # worker_image="my-registry.practicus.my-company.com/demo/practicus-minimal-my:24.8.3",
    # or else, the current Practicus AI platform version is used
    worker_image="my-registry.practicus.my-company.com/demo/practicus-minimal-my",
    worker_size="Small-restricted",
    image_config=image_config,
)

worker_from_custom_image = prt.create_worker(worker_config)
worker_from_custom_image.open_notebook()
```

With that, you have a Practicus AI Worker running your own container image. You can install packages, train models, or run any workload you need.

<!-- #region -->
## Advanced Topics

- **Privileged vs. Restricted Builder**: Practicus AI offers a restricted builder `ghcr.io/practicusai/practicus-builder`  by default. If you have use cases requiring lower-level system access, admins can enable a privileged builder `ghcr.io/practicusai/practicus-builder-privileged` via the **Security Context** of the Worker Size.

- **Custom Builder Images**: You can create a custom Alpine builder image (e.g., to install specialized dependencies or certificates) and set `custom_builder_url` in your `ImageConfig`. This allows even more flexibility for specialized builds.

- **Pull vs. Push Credentials**: If you need separate credentials for pulling a base image and pushing a built image, you can first build (and cache) the base image locally without pushing (`push_image=False`), then change the credentials and re-run the build with push enabled.

Below is an example snippet for using a custom builder:

```python
import practicuscore as prt

image_config = prt.ImageConfig(
    builder=True,
    custom_builder_url="my-registry.practicus.my-company.com/my-builders/practicus-builder:24.8.3",
    # ...other parameters...
)

worker_config = prt.WorkerConfig(
    image_config=image_config,
    # ...other parameters...
)

worker = prt.create_worker(worker_config)
```

<!-- #endregion -->

```python
# Clean-up
builder_worker.terminate()
worker_from_custom_image.terminate()
```


---

**Previous**: [Llms With DeepSpeed](../distributed-computing/deepspeed/llm-fine-tuning/llms-with-deepspeed.md) | **Next**: [Automate Notebooks > Executing Notebooks](automate-notebooks/executing-notebooks.md)
