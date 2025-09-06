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

# Building and Using Custom Container Images

In this example, we'll demonstrate how to build custom container images using the Practicus AI platform. You'll see how to:

1. **Start a Worker** with container-building capabilities.
2. **Create and push a custom container image** to a private registry.
3. **Use your custom container** to run new Practicus AI Workers.

We'll also cover:

- Configuring the builder to allocate a percentage of your Worker's resources.
- Pushing images to the Practicus AI container registry or other registries.
- Granting security permissions to allow custom images.
- **Advanced topics** like using insecure registries and custom build configurations, privileged builds, custom builder images, and separating credentials for pulling vs. pushing.

## Step 1: Start a Worker with Image-Building Capabilities

First, we'll create a Practicus AI Worker that can build container images. This Worker uses two containers:

1. **Primary Container (Ubuntu Linux):** Contains your main environment.
2. **Builder Container (Alpine Linux):** Builds container images under the hood.

By setting `builder=True` in `ImageConfig`, you opt to start this secondary container. You can also specify how much of your Worker's CPU/RAM/GPU the builder can use.

```python
import practicuscore as prt

# Configure a Worker that can build container images.
image_config = prt.ImageConfig(
    builder=True,  # Enables the builder container.
    # Optional: allocates 60% of CPU/RAM/GPU to the builder.
    # builder_capacity=60,
)

worker_config = prt.WorkerConfig(
    worker_image="practicus-minimal",
    worker_size="Medium-restricted",
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

Below, we create a small text file and a simple Dockerfile, then build and push the image.

```python
# Create a text file in ~/build
with open("/home/ubuntu/build/hello.txt", "wt") as f:
    f.write("Hello from the custom container image!")
```

```python
# Create a Dockerfile in ~/build
dockerfile_content = """
# Use a base image from your private registry or a public source
FROM my-registry.practicus.my-company.com/practicusai/practicus-minimal:25.5.3

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
# Build and push the image, run on a builder Worker.
import practicuscore as prt

repo_username = "some-user-name"
repo_password = "some-token"

success = prt.containers.build_image(
    name="my-registry.practicus.my-company.com/demo/practicus-minimal-my",
    tag="25.5.3",
    push_image=True,
    registry_credentials=[
        ("my-registry.practicus.my-company.com", repo_username, repo_password),
    ],
    # Optional: use HTTP instead of HTTPS if you are using an on-prem registry and haven't installed certificates to the builder image.
    # insecure_registry=True,
)

print("Successful!" if success else "Failed..")
```

Once your image is successfully pushed, you can reference it in any future Practicus AI Worker by its full name, for example:

```
my-registry.practicus.my-company.com/demo/practicus-minimal-my:25.5.3
```



## Step 3: Use the Custom Image you just built

Switch back to your original environment (the one where you created `builder_worker`). Now you can create a new Worker that runs on your freshly built image. Make sure your user or group has permissions to use custom container images. If you're an admin, you can grant this permission in the Practicus AI admin console under **Infrastructure** > **Container Images**.

Below is an example of how to run a Worker with the newly built image:


```python
import practicuscore as prt

image_config = prt.ImageConfig(repo_username="some-user-name", repo_password="some-token")

worker_config = prt.WorkerConfig(
    # If desired, specify a tag explicitly,
    # worker_image="my-registry.practicus.my-company.com/demo/practicus-minimal-my:25.5.3",
    # or else, the current Practicus AI platform version is used if the tag is omitted.
    worker_image="my-registry.practicus.my-company.com/demo/practicus-minimal-my",
    worker_size="Medium",
    image_config=image_config,
)

worker_from_custom_image = prt.create_worker(worker_config)
worker_from_custom_image.open_notebook()
```

With that, you have a Practicus AI Worker running your custom container image. You can install packages, train models, or run any workload you need.



## Step 4: Configure build service (if needed)

After starting your builder Worker, you may need to configure the build service to work with your specific environment. The most common configuration is for using private SSL certificates or using insecure registries (registries that use HTTP instead of HTTPS), but you can also configure mirrors, and other advanced settings.

There are two approaches: a simple one for just configuring insecure registries, and an advanced one for complete build service configuration.

```python
import practicuscore as prt

# Simple approach: Just specify insecure registries
prt.containers.update_build_config(
    insecure_registries="my-registry.practicus.my-company.com,another-registry.example.com"
)
```

### Custom build configuration (Optional)

For more complex scenarios, such as custom certificates, registry mirrors, or performance tuning, you can provide a complete build configuration:

```python
# Advanced approach: Full custom build configuration
custom_config = """
[registry."my-registry.practicus.my-company.com"]
  insecure = true
  
[registry."secure-registry.example.com"]
  # With custom CA certificates
  ca=["/usr/local/share/ca-certificates/prt-ca-bundle.crt"]
"""

# Note: If your admin enabled private certificate injection,
# Practicus AI will automatically mount /usr/local/share/ca-certificates/prt-ca-bundle.crt
# on the Alpine image builder container.
prt.containers.update_build_config(config_content=custom_config)
```

<!-- #region -->
## Advanced Topics

### Dynamic Build Configuration

You've already seen how to dynamically configure build configurations for insecure registries or with custom settings. Here are some additional configuration examples:

- **Registry with Client Certificates**:
  ```
  [registry."secure-registry.example.com"]
    ca=["/usr/local/share/ca-certificates/prt-ca-bundle.crt"]
    client=["/etc/ssl/certs/client-cert.pem", "/etc/ssl/private/client-key.pem"]
  ```

- **Registry Mirrors** (for faster pulls):
  ```
  [registry."registry-1.docker.io"]
    mirrors=["https://mirror1.example.com", "https://mirror2.example.com"]
  ```

- **Performance Tuning**:
  ```
  [worker.oci]
    max-parallelism=8
    snapshotter="overlayfs"
    gc=true
  ```

### Private Certificates

If Practicus AI administrators have enabled private certificate injection, the certificate bundle file will be mounted at `/usr/local/share/ca-certificates/prt-ca-bundle.crt` within the Alpine image builder container.

You can directly use this mounted certificate file, or alternatively, copy the certificates into the `~/build` directory. The `~/build` directory is shared between your primary notebook container and the Alpine builder image and is mounted as `/build` on the Alpine container.

### Privileged vs. Restricted Builder

Practicus AI provides a restricted builder (`ghcr.io/practicusai/practicus-builder`) by default. For tasks requiring lower-level system access, such as building specific drivers, administrators can enable a privileged builder (`ghcr.io/practicusai/practicus-builder-privileged`). This setting can be managed through the **Security Context** option under Worker Size.

### Automated Certificate Injection

If Practicus AI administrators have enabled private certificate injection and you are using the privileged worker option, Practicus AI will automatically run certificate installation procedures on the Alpine builder. Note that automated certificate installation is not available for the restricted (unprivileged) worker.

### Custom Builder Images

You can create a custom Alpine builder image (e.g., to install specialized dependencies or certificates) and set `custom_builder_url` in `ImageConfig`. This allows more flexibility for specialized builds.

### Pull vs. Push Credentials

If you need separate credentials for pulling a base image and pushing a built image, you can:
1. Build (and cache) the base image locally without pushing (`push_image=False`).
2. Change your credentials.
3. Re-run the build with `push_image=True`, which will use the cached image you pulled previously.

### Integrating with CI/CD

You can include container builds in your Practicus AI CI/CD workflows. For instance, automatically build and push your image upon each commit by referencing these steps in your `.github/workflows/` YAML.

### Building with CLI

You can also build and push containers using the Practicus AI CLI, which can be helpful in automation scenarios.

Example CLI command:
```bash
prtcli build-container-image -p \
    name="my-registry.practicus.my-company.com/my-project/my-image" \
    tag="25.5.3" \
    build_args="{\"ENV_VAR\": \"value\"}" \
    registry_credentials="[(\"my-registry.practicus.my-company.com\", \"my-robot-user\", \"token\")]"
```

<!-- #endregion -->

```python
# Clean up
builder_worker.terminate()
worker_from_custom_image.terminate()
```


---

**Previous**: [Git Integrated CICD](git-integrated-cicd.md) | **Next**: [Notifications](notifications.md)
