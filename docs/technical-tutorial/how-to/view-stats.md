---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

# System Resource Usage

Below is a sample code snippet that retrieves and displays system resource usage of memory, disk, and GPU statistics. This helps you monitor available system resources at a glance:

- **Memory**: Reports total, free, and percentage of free memory.
- **Disk**: Reports total, free, and percentage of free disk space.
- **GPU**: Shows detailed GPU memory usage (used, reserved, total).

```python
from practicuscore.util import Stats

total_mem, used_mem = Stats.get_memory_stats()

free_mem = total_mem - used_mem
gb = 1024**3
total_mem_gb = round(total_mem / gb, 2)
free_mem_gb = round(free_mem / gb, 2)
free_mem_percent = round(free_mem / total_mem * 100, 2)

print(f"Worker RAM : {total_mem_gb} GB")
print(f"Free RAM : {free_mem_gb} GB ({free_mem_percent}%)\n")

total_disk, free_disk = Stats.get_disk_stats()

total_disk_gb = round(total_disk / gb, 2)
free_disk_gb = round(free_disk / gb, 2)
free_disk_percent = round(free_disk / total_disk * 100, 2)

print(f"Worker Disk : {total_disk_gb} GB")
print(f"Free Disk : {free_disk_gb} GB ({free_disk_percent}%)")

print("Note: The above views the physical disk capacity of the node.")
print("The ephemeral disk capacity that your admin allowed for this Worker can be lower.\n")

try:
    gpu_stats = Stats.get_gpu_stats()
    for gpu_id, (used, reserved, total) in enumerate(gpu_memory):
        print(f"GPU usage for gpu: {gpu_id} used: {used} reserved: {reserved} total: {total}")
except:
    print("No GPUs detected")
```


---

**Previous**: [Share Workers](share-workers.md) | **Next**: [Startup Scripts](startup-scripts.md)
