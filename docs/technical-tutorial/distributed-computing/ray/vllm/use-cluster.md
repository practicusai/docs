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

# Using the interactive Ray Cluster for vLLM

- This example demonstrates how to connect to the Practicus AI Ray cluster we created, and execute vLLM + Ray operations.
- Please run this example on the `Ray Coordinator (master)`.

```python
import practicuscore as prt

# Let's get a Ray session.
# this is similar to running `import ray` and then `ray.init()`
ray = prt.distributed.get_client()
```

```python
from vllm import LLM, SamplingParams

prompts = [
    "Mexico is famous for ",
    "The largest country in the world is ",
]

sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
llm = LLM(model="facebook/opt-125m")
responses = llm.generate(prompts, sampling_params)

for response in responses:
    print(response.outputs[0].text)
```

### Ray Dashboard

Practicus AI Ray offers an interactive dashboard where you can view execution details. Let's open the dashboard.

```python
dashboard_url = prt.distributed.open_dashboard()

print("Page did not open? You can open this url manually:", dashboard_url)
```

```python
# Let's close the session
ray.shutdown()
```

<!-- #region -->
### Terminating the cluster

- You can go back to the other worker where you created the cluster to run:

```python
coordinator_worker.terminate()
```
- Or, terminate "self" and children workers with the below:

```python
prt.get_local_worker().terminate()
```

### Troubleshooting

If you’re experiencing issues with an interactive cluster that doesn’t run job/train.py, please follow these steps:

1. **Agent Count Mismatch**:
   If the number of distributed agents shown by `prt.distributed.get_client()` is less than what you expected, wait a moment and then run `get_client()` again. This is usually because the agents have not yet joined the cluster.
   *Note: Batch jobs automatically wait for agents to join.*

2. **Viewing Logs**:
   To view logs, navigate to the `~/my/.distributed` folder.
<!-- #endregion -->


---

**Previous**: [Start Cluster](start-cluster.md) | **Next**: [Custom Adaptor > Start Cluster](../../custom-adaptor/start-cluster.md)
