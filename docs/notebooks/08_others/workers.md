---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

###  Practicus AI Workers 

Practicus AI Workers live in a Practicus AI region and you can create, work with and terminate them as the below.


#### Simple use of workers

```python
import practicuscore as prt

# Workers are created under a Practicus AI region
region = prt.current_region()

# You can also connect to a remote region instead of the default one
# region = prt.get_region(..)
```

```python
# Let's view our region
region
```

```python
# The below is the easiest way to start working with a worker 
worker = region.get_or_create_worker()
```

```python
# Let's view worker details
worker
```

```python
# Let's load a sample file on the Worker
some_data_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/ice_cream.csv"
}
with worker.load(some_data_conn) as proc:
    df = proc.get_df_copy()
    # Exiting the 'with' will free up the process
```

```python
# The rest is business as usual..
df
```

#### Behind the scenes..

```python
# Let's break down what the below code actually does
# worker = region.get_or_create_worker()

if prt.running_on_a_worker():
    print("Since I am already running on a worker, let's use this one!")
    worker = prt.get_local_worker()
else:
    print("I am running on my laptop, let's get a worker.")
    print("Do I already have running workers?")
    if len(region.worker_list) > 0:
        print("Yes, I do have workers, let's use one of them.")
        worker = region.worker_list[0]
        # The real code is actually a bit smarter,
        # it will give the worker with the max memory
    else:
        print("I don't have a worker. Let's create a new one!")
        worker = prt.create_worker()

print("My worker details:")
worker
```

```python
# Always terminate the workers once you are done

if prt.running_on_a_worker():
    print("The worker is terminating itself..")
    print("Please make sure you are not losing any active workon this worker.")

worker.terminate()
```

#### Customizing workers

```python
# We can choose the size, container image and also configure other parameters
worker_config = {
    "worker_size": "X-Small",
    "worker_image": "practicus",
    # # Assign distributed worker settings
    # "distributed_conf_dict": {
    #     "max_count": 0,
    #     "initial_count": 0,
    #     "memory_mb": 1024
    # },
    # # To enforce image pull policy to Always, make the below True
    # # Only use in dev/test where you cannot easily upgrade image versions
    # "k8s_pull_new_image": False,
    # # To skip SSL verification
    # # Only use in dev/test and for self signed SSL certificates
    # "bypass_ssl_verification": False
}
worker = region.create_worker(worker_config)
```

```python
# If you do not know which worker sizes you have access to:
region.worker_size_list.to_pandas()
```

```python

```

```python
# If you do not know which worker container images you have access to:
region.worker_image_list.to_pandas()
```

```python
# Let's iterate over workers
for worker in region.worker_list:
    print("Worker details:", worker)
```

```python
# We can also realod workers.
# This is useful if you create workers from multiple systems
region.reload_worker_list()
```

```python
# Converting the worker_list into string will give you a csv 
print(region.worker_list)
```

```python
# You can also get workers as a pandas DataFrame for convenience
region.worker_list.to_pandas()
```

```python
# Simply accessing the worker_list will print a formatted table string 
region.worker_list
```

```python
first_worker = region.worker_list[0]
# Accessing an worker object will print it's details
first_worker
```

```python
worker_name = first_worker.name
print("Searching for:", worker_name)
# You can locate a worker using it's name
worker = region.get_worker(worker_name)
print("Located:", worker)
# Or using worker index only, e.g. 123 for Worker-123
# region.get_worker(123)
```

### Worker Logs

```python
# You can view worker logs like the below 
worker.view_logs()

# To get logs as a string 
worker_logs = worker.get_logs()

# E.g. to search for an error string
print("some error" in worker_logs)
```

### Cleaning up

```python
# There are multiple ways to terminate a worker.
worker.terminate()
# Or, 
# region.terminate_worker(worker_name)
# Worker number works too
# region.terminate_worker(123)
```

```python
# The below will terminate all of your workers
region.terminate_all_workers()
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

**Previous**: [Test Core Features](tests/test_core_features.md) | **Next**: [Model Foundation](model_foundation.md)
