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

# Distributed DeepSpeed Training

This example demonstrates the process of setting up distributed workers for distributed training using Practicus AI DeepSpeed.

Focuses:
- Configuring and launching distributed workers using Practicus AI.
- Monitoring and logging distributed job performance and resource usage.
- Terminating the distributed job after completion.

The train.py script and ds_config.json configuration files are used to define the model fine-tuning process.


#### Importing Libraries and Configuring Distributed Job

This step imports the required libraries, including `practicuscore`, and sets up the configurations for a distributed job. The key elements are:
- `job_dir`: Directory containing DeepSpeed configuration files and the training script.
- `DistJobConfig`: Defines distributed job parameters such as worker count and termination policy.
- `WorkerConfig`: Specifies worker parameters, including the Docker image, worker size, and startup script.

The configuration prepares a coordinator worker that initializes a distributed job.

### Before you begin
- Create "deepspeed" under your "~/my" folder.
- And copy `train.py` and `ds_config.json` under this folder.

```python
worker_size = "L-GPU"
worker_count = None
log_level = "DEBUG"
worker_image = "ghcr.io/practicusai/practicus-gpu-deepspeed"
terminate_on_completion = False
create_deepspeed_folder = False
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert log_level, "Please enter your log_level."
assert worker_image, "Please enter your worker_image."
assert terminate_on_completion, (
    "Please enter your terminate_on_completion (True or False)."
)
assert create_deepspeed_folder, "Please enter your create_spark_folder (True or False)."
```

```python
import os
import shutil

if create_deepspeed_folder:
    # Define source and destination
    source_dir = "samples/notebooks/05_distributed_computing/04_deepspeed/01_basics"
    train_file = f"{source_dir}/train.py"
    config_file = f"{source_dir}/ds_config.json"

    # Move it to '~/my', which is your persistent home directory.
    job_dir = os.path.expanduser("~/my/deepspeed")
    train_dest_file = f"{job_dir}/train.py"
    config_dest_file = f"{job_dir}/ds_config.json"

    # Copy the job file to the shared location
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)

    print(f"Copying file from '{train_file}' to '{train_dest_file}'...")
    print(f"Copying file from '{config_file}' to '{config_dest_file}'...")
    try:
        shutil.copy(train_file, train_dest_file)
        shutil.copy(config_file, config_dest_file)
        print("✅ Copy successful.")
    except FileNotFoundError:
        print(f"❌ Error: Could not find source file at {train_file} or {config_file}")
else:
    # DeepSpeed job directory must have default files ds_config.json and train.py (can be renamed)
    job_dir = "~/my/deepspeed"
```

```python
import practicuscore as prt

distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.deepspeed,
    job_dir=job_dir,
    worker_count=worker_count,
    terminate_on_completion=False,
)

worker_config = prt.WorkerConfig(
    worker_image=worker_image,
    worker_size=worker_size,
    log_level=log_level,
    distributed_config=distributed_config,
)

coordinator_worker = prt.create_worker(worker_config)

job_id = coordinator_worker.job_id

assert job_id, "Could not create distributed job"
```

### Monitoring Distributed Job

The `live_view` and `view_log` utilities from the Practicus SDK are used to monitor the progress of the distributed job. This provides details such as:
- Job ID, start time, worker states, and GPU utilization.
- Resource allocation for each worker in the distributed cluster.

It helps in tracking the real-time status of the distributed job.

```python
# Live resource allocation
prt.distributed.live_view(job_dir, job_id)
```

```python
# For master logs, you can check Rank-0 logs:
prt.distributed.view_log(job_dir, job_id, rank=0)
```

```python
# For pair logs, you must specify pair IDs, e.g. 1:
prt.distributed.view_log(job_dir, job_id, rank=1)
```

### Terminating Distributed Job Cluster

The distributed job cluster and all associated workers are terminated using the `terminate` method of the coordinator worker.

```python
coordinator_worker.terminate()
```


## Supplementary Files

### ds_config.json
```json
{
    "train_batch_size": 4,
    "gradient_accumulation_steps": 2,
    "optimizer": {
        "type": "Adam",
        "params": {
            "lr": 0.001
        }
    },
    "fp16": {
        "enabled": true
    },
    "zero_optimization": {
        "stage": 1
    }
}

```

### train.py
```python
import torch
import torch.nn as nn
import deepspeed
import torch.distributed as dist
import os
import json


# Define a dummy large neural network
class LargeModel(nn.Module):
    def __init__(self):
        super(LargeModel, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(8192, 4096),
            nn.ReLU(),
            nn.Linear(4096, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x):
        return self.layers(x)


# Function to check FP16
def is_fp16_enabled(config_path="ds_config.json"):
    with open(config_path) as f:
        config = json.load(f)
    return config.get("fp16", {}).get("enabled", False)


# Main training function
def train():
    # Distributed setup
    dist.init_process_group(
        backend="nccl",
        init_method=f"tcp://{os.environ['MASTER_ADDR']}:{os.environ['MASTER_PORT']}",
        rank=int(os.environ["RANK"]),
        world_size=int(os.environ["WORLD_SIZE"]),
    )

    device = torch.device(f"cuda:0")
    model = LargeModel().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Initialize DeepSpeed
    model, optimizer, _, _ = deepspeed.initialize(model=model, optimizer=optimizer, config="ds_config.json")

    # Training loop
    for epoch in range(5):
        optimizer.zero_grad()

        # Creation of dummy train data
        data = torch.randn(32768, 8192).to(device)
        target = torch.randn(32768, 1).to(device)

        # Convert data and target to FP16 if enabled
        if is_fp16_enabled("ds_config.json"):
            data, target = data.half(), target.half()

        # Log memory usage and loss
        loss = nn.MSELoss()(model(data), target)
        model.backward(loss)
        model.step()

        print(
            f"[GPU {os.environ['RANK']}] Epoch {epoch}, Loss: {loss.item()}, "
            f"Allocated VRAM: {torch.cuda.memory_allocated(device) / 1e9:.2f} GB"
        )

    # Clean cache
    dist.destroy_process_group()


if __name__ == "__main__":
    train()

```


---

**Previous**: [XGBoost](../../dask/distributed-training/xgboost.md) | **Next**: [LLM Fine Tuning > Llms With DeepSpeed](../llm-fine-tuning/llms-with-deepspeed.md)
