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

# Advanced GPU Resource Management with Practicus AI

This document provides an overview of how to configure partial NVIDIA GPUs (MIG), along with high-level steps for AMD and Intel GPU support, and how Practicus AI platform facilitates GPU management.

### Topics covered in this document
- Partial NVIDIA GPUs (MIG)
- AMD GPUs
- Intel GPUs

---

## 1. **Partial NVIDIA GPUs (MIG)**

### **How MIG Works**
- NVIDIA's `Multi-Instance GPU (MIG)` feature allows you to split a single physical GPU (e.g., NVIDIA A100m, H100, H200) into multiple independent GPU instances.
- Each MIG instance provides dedicated memory and compute resources, ideal for running multiple workloads on the same GPU.

### **Setup Steps**
1. **Enable MIG Mode on the GPU**:
   - Log into the GPU node and enable MIG using `nvidia-smi`:
     ```bash
     sudo nvidia-smi -i 0 --mig-enable
     sudo reboot
     ```
   - After reboot, confirm MIG mode is enabled:
     ```bash
     nvidia-smi
     ```

2. **Create MIG Instances**:
   - Use `nvidia-smi` to create MIG profiles. For example, split a GPU into 7 instances:
     ```bash
     sudo nvidia-smi mig -i 0 -cgi 0,1,2,3,4,5,6
     sudo nvidia-smi mig -i 0 -cci
     ```
   - Check the configuration:
     ```bash
     nvidia-smi
     ```

3. **Expose MIG Resources in Kubernetes**:
   - Deploy the NVIDIA Device Plugin:
     ```bash
     kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/deployments/k8s-device-plugin-daemonset.yaml
     ```
   - Verify available resources:
     ```bash
     kubectl describe node <node-name>
     ```

- To learn more please visit:
    - https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-operator-mig.html

---

## 2. **Custom GPU Configuration in Practicus AI**

Practicus AI simplifies advanced GPU management through the intuitive management UI:

**Open Practicus AI Management Console**:
- Access the platform's web console for infrustructure management.

**Select Worker Sizes**:
- Choose from predefined worker sizes or create a new one to include GPU capacity :
   - `Number of GPUs`
   - `Amount of Video RAM (VRAM)`

**Enter GPU Type Selector**:
- Specify the custom GPU type you need:
    - Specify for Nvidia MIG (e.g. `nvidia.com/mig-1g.5gb`) you defined in the above step.
    - Specify for other vendors (e.g., `amd.com/gpu` or `intel.com/gpu`).
    - Leave empty for the default, which will use entire NVDIA GPUs without fractions.

**Deploy workloads as usual**:
- Deploy end user workers, model hosts, app hosts etc. as usual with the worker size you defined above.
- The platform will dynamically manage the resources with the selected GPU configuration.

**Example Configuration**

- If you set GPU count to 2, with a GPU type selector of `nvidia.com/mig-1g.5gb` running on a single ``NVIDIA H100 GPU``, the end user could get **two separate GPU instances**, each with **1/7th of the GPU's compute and memory resources (1 compute slice and 5 GB of memory per instance)**.
- This configuration allows the same physical GPU to handle multiple workloads independently, providing dedicated resources for each workload without interference. 
- This setup is ideal for lightweight GPU workloads, such as inference or smaller-scale training tasks, that do not require the full power of an entire GPU.

**Important Note**  
- Please note that the VRAM setting in the **Practicus AI Management Console** does **not** dictate how much VRAM a user gets. It is only used to **measure usage** and ensure a user is kept within their designated daily/weekly/monthly usage limits. 
- To actually **enforce VRAM limits**, you must use **NVIDIA MIG profiles** (e.g., `nvidia.com/mig-1g.5gb`) or equivalent to `apply resource constraints at the hardware level.`

---

## 3. **High-Level Steps for AMD GPUs**

AMD GPUs (e.g., using ROCm) require setup similar to NVIDIA but with their own tools and configurations:

1. **Install AMD ROCm Drivers**:
   - Install ROCm drivers on the nodes with AMD GPUs.

2. **Deploy AMD Device Plugin**:
   - Use the AMD ROCm Kubernetes device plugin to expose AMD GPU resources:
     ```bash
     kubectl apply -f https://github.com/RadeonOpenCompute/k8s-device-plugin
     ```

The rest is the same as NVIDIA MIG, define a new worker size and use the GPU Type Selector `amd.com/gpu`

---

## 4. **High-Level Steps for Intel GPUs**

Intel GPUs can be managed using the Intel GPU Device Plugin:

1. **Install Intel GPU Drivers**:
   - Install Intel drivers and libraries for iGPU or discrete GPU support.

2. **Deploy Intel Device Plugin**:
   - Use the Intel GPU plugin to expose GPU resources:
     ```bash
     kubectl apply -f https://github.com/intel/intel-device-plugins-for-kubernetes
     ```
The rest is the same as NVIDIA MIG, define a new worker size and use the GPU Type Selector `intel.com/gpu`

```python

```


## Supplementary Files

### code_quality/bad_code.py
```python
import pandas 

# this is an error
print(undefined_var)




print("Too many blank lines, which is code formatting issue.")

```

### deploy_llm/model.py
```python
import sys
from datetime import datetime

generator = None
answers = ""


async def init(model_meta=None, *args, **kwargs):
    global generator
    if generator is not None:
        print("generator exists, using")
        return

    print("generator is none, building")

    # Assuming llama library is copied into cache dir, in addition to torch .pth files
    llama_cache = "/var/practicus/cache"
    if llama_cache not in sys.path:
        sys.path.insert(0, llama_cache)
        
    try:
        from llama import Llama
    except Exception as e:
        raise ModuleNotFoundError("llama library not found. Have you included it in the object storage cache?") from e
    
    try:
        generator = Llama.build(
            ckpt_dir=f"{llama_cache}/CodeLlama-7b-Instruct/",
            tokenizer_path=f"{llama_cache}/CodeLlama-7b-Instruct/tokenizer.model",
            max_seq_len=512,
            max_batch_size=4,
            model_parallel_size=1
        )
    except:
        building_generator = False
        raise


async def cleanup(model_meta=None, *args, **kwargs):
    print("Cleaning up memory")

    global generator
    generator = None

    from torch import cuda
    cuda.empty_cache()


def _predict(http_request=None, model_meta=None, payload_dict=None, *args, **kwargs):
    start = datetime.now()
    
    # instructions = [[
    #     {"role": "system", "content": payload_dict["system_context"]},
    #     {"role": "user", "content": payload_dict["user_prompt"]}
    # ]]

    instructions = [[
        {"role": "system", "content": ""},
        {"role": "user", "content": "Capital of Turkey"}
    ]]

    results = generator.chat_completion(
        instructions,
        max_gen_len=None,
        temperature=0.2,
        top_p=0.95,
    )

    answer = ""
    for result in results:
        answer += f"{result['generation']['content']}\n"

    print("thread answer:", answer)
    total_time = (datetime.now() - start).total_seconds()
    print("thread asnwer in:", total_time)    

    global answers 
    answers += f"start:{start} end: {datetime.now()} time: {total_time} answer: {answer}\n"


async def predict(http_request, model_meta=None, payload_dict=None, *args, **kwargs):
    await init(model_meta)
    
    import threading 
    
    threads = []

    count = int(payload_dict["count"])
    thread_start = datetime.now()
    for _ in range(count):
        thread = threading.Thread(target=_predict)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    print("Total finished in:", (datetime.now() - thread_start).total_seconds())    

    return {
        "answer": f"Time:{(datetime.now() - thread_start).total_seconds()}\nanswers:{answers}"
    }
    

```

### sdk_preprocess_tutorial/snippets/impute_missing_knn.py
```python
from enum import Enum


class WeightsEnum(str, Enum):
    uniform = "uniform"
    distance = "distance"


def impute_missing_knn(df, missing_val_col: list[str] | None, n_neighbors: int = 5, weights: WeightsEnum = WeightsEnum.uniform):
    """
    Replaces each missing value using K-Nearest Neighbors technique
    :param missing_val_col: Columns to impute missing values. Leave empty for all columns
    :param n_neighbors: Number of neighboring samples to use for imputation.
    :param weights: Weight function used in prediction
    """
    import pandas as pd
    import numpy as np
    from sklearn.impute import KNNImputer

    knn_imp = KNNImputer(n_neighbors=n_neighbors, weights=str(weights))

    numeric_df = df.select_dtypes(include=[np.number])

    if missing_val_col:
        non_numeric_columns = set(missing_val_col) - set(numeric_df.columns)
        if non_numeric_columns:
            raise ValueError(f"Please only select numeric columns to impute, or do not select any columns. Non-numeric columns: {non_numeric_columns}")

        imputed_data = knn_imp.fit_transform(numeric_df[missing_val_col])
        imputed_df = pd.DataFrame(imputed_data, columns=missing_val_col, index=numeric_df.index)
    else:
        imputed_data = knn_imp.fit_transform(numeric_df)
        imputed_df = pd.DataFrame(imputed_data, columns=numeric_df.columns, index=numeric_df.index)

    df.update(imputed_df)
    return df


impute_missing_knn.worker_required = True
impute_missing_knn.supported_engines = ['pandas']

```

### sdk_preprocess_tutorial/snippets/normalize.py
```python
from enum import Enum


class NormalizationOptions(str, Enum):
    Z_SCORE = "Z-Score Normalization"
    MIN_MAX = "Min-Max Normalization"
    ROBUST = "Robust Normalization"


def normalize(df, numeric_col_list: list[str] | None = None, normalization_option: NormalizationOptions = NormalizationOptions.Z_SCORE, result: list[str] | None = None):
    """
    Normalizes certain columns in the DataFrame with the selected normalization method.
    
    :param numeric_col_list: Names of the numeric columns to normalize. If None, all numeric columns are considered.
    :param normalization_option: Specifies the method for normalization: Z-Score (standardizes data), Min-Max (scales data to a fixed range, typically [0, 1]), or Robust (reduces the impact of outliers).
    :param result: Column names to write normalization results. If None, the original column names appended with "_normalized" will be used.
    """
    import numpy as np
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    
    # If no specific columns provided, use all numeric columns
    if numeric_col_list is None:
        numeric_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    # Process according to the selected normalization method
    if normalization_option == NormalizationOptions.Z_SCORE:
        scaler = StandardScaler()
    elif normalization_option == NormalizationOptions.MIN_MAX:
        scaler = MinMaxScaler()
    elif normalization_option == NormalizationOptions.ROBUST:
        scaler = RobustScaler()
    else:
        raise ValueError("Unsupported normalization option selected.")
    
    # Normalize specified columns and assign results either to new columns or overwrite them
    for col in numeric_col_list:
        normalized_col_name = col + "_normalized" if result is None else result.pop(0) if result else f"{col}_normalized"
        df[normalized_col_name] = scaler.fit_transform(df[[col]])

    return df


normalize.worker_required = True
```

### sdk_preprocess_tutorial/snippets/suppress_outliers.py
```python
def suppress_outliers(
        df, outlier_float_col_list: list[str] | None, q1_percentile: float = 0.25, q3_percentile: float = 0.75,
        result_col_suffix: str | None = "no_outlier", result_col_prefix: str | None = None):
    """
    Suppresses outliers in specified numeric columns of the dataframe based on custom percentile values for Q1 and Q3.
    Adds new columns with the selected suffix or prefix. If no suffix or prefix is provided, overwrites the existing column.
    :param outlier_float_col_list: List of numeric columns to check for outliers. If left empty, applies to all numeric columns.
    :param q1_percentile: Custom percentile for Q1 (e.g., 0.25 for 25th percentile).
    :param q3_percentile: Custom percentile for Q3 (e.g., 0.75 for 75th percentile).
    :param result_col_suffix: Suffix for the new column where the suppressed data will be stored.
    :param result_col_prefix: Prefix for the new column where the suppressed data will be stored.
    """
    import numpy as np

    # If no specific columns provided, use all numeric columns
    if not outlier_float_col_list:
        outlier_float_col_list = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(outlier_float_col_list) == 0:
        raise ValueError("No numeric column provided or located.")

    # Process each specified column
    for col in outlier_float_col_list:
        q1 = df[col].quantile(q1_percentile)
        q3 = df[col].quantile(q3_percentile)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if result_col_suffix:
            new_col_name = f'{col}_{result_col_suffix}'
        elif result_col_prefix:
            new_col_name = f'{result_col_prefix}_{col}'
        else:
            new_col_name = col

        # Create a new column (or override), with suppressed values
        df[new_col_name] = np.where(
            df[col] < lower_bound, lower_bound, np.where(df[col] > upper_bound, upper_bound, df[col])
        )
    
    return df

```


---

**Previous**: [Use Cluster](../07_distributed_computing/01_spark/03_auto_scaled/02_use_cluster.md) | **Next**: [Processes](processes.md)
