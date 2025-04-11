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
