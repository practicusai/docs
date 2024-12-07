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

### Practicus AI Data Catalog

Practicus AI provides a Data Catalog where you, or an admininstrator can save data source connection information. 

Data sources can be Data Lakes, Object Storage (E.g. S3), Data Warehouses (E.g. Snowflake), Databases (e.g. Oracle) ...

Data catalog info does **not** include details like the actual SQL queries to run, S3 keys to read etc., but just the info such as host address, port (if needed), user name, password etc. You can think of them as a "connection string" in most programming languages. 

```python
import practicuscore as prt

# Connections are saved under a Practicus AI region
region = prt.current_region()

# You can also conenct to a remote region instead of the default one
# region = prt.regions.get_region(..)
```

```python
# Let's get connections that we have access to 
# If a connection is missing, please ask your admin to be granted access,
# OR, create new connections using the Practicus AI App or SDK
connections = region.connection_list

if len(connections) == 0:
    raise ConnectionError(
        "You or an admin has not defined any conenctions yet. "
        "This notebook will not be meanignful..")
```

```python
# Let's view our connections as a Pandas DF for convenience
connections.to_pandas()
```

```python
# Lets view the first connection
first_connection = connections[0]
first_connection
```

```python
# Is the data source read-only? 
if first_connection.can_write:
    print("You can read from, and write to this data source.")
else:
    print("Data source is read-only. You cannot write to this data-source.")
    # Note: read-only data sources are created by Practicus AI admins 
    # and shared with users or user groups using Management Console.
```

```python
# You can search a connection using it's uuid
print("Searching with connection uuid:", first_connection.uuid)
found_connection = region.get_connection(first_connection.uuid)
print("Found:", found_connection)
```

```python
# You can also search using the connection name.
# Please note that connection names can be updated later,
#   and they are not unique in the Data Catalog.
# Please prefer to search using a connection uuid for production deployments.
print("Searching with connection name:", first_connection.name)
found_connection = region.get_connection(first_connection.name)
print("Found:", found_connection)
```

#### Deep dive into connections

There are multiple ways to load data into a Practicus AI process. 

Lets' start with the simplest, just using a dictionary, and then we will discuss other options including the Data Catalog.


#### Loading data without the data catalog

This is the simplest option and does not use a central data catalog to store connections. If you have the database credentials, you can read from that database.

```python
# Let's get a worker to use, one that you are already working on, or a remote one.
try:
    worker = region.get_local_worker()
except: 
    workers = region.worker_list
    if len(workers) == 0:
        raise ConnectionError(
            "Please run this code on a Practicus AI worker, or have at least one active worker") 
    worker = workers[0]
```

```python
# Let's load using the sample SQLLite DB that comes pre-installed with Practicus AI
sql_query = """
  select artists.Name, albums.Title 
  from artists, albums 
  where artists.ArtistId = albums.ArtistId 
  limit 1000
"""

# Let's configure a connection
conn_conf_dict = {
    "connection_type": "SQLITE",
    "file_path": "/home/ubuntu/samples/chinook.db",
    "sql_query": sql_query,
}

proc = worker.load(conn_conf_dict)
proc.show_head()
proc.kill()
```

```python
# Connection configuration can be a json
import json

conn_conf_json = json.dumps(conn_conf_dict)

proc = worker.load(conn_conf_json)
proc.show_head()
proc.kill()
```

```python
# Connection configuration can be path to a json file
with open("my_conn_conf.json", "wt") as f:
    f.write(conn_conf_json)

proc = worker.load("my_conn_conf.json")
proc.show_head()
proc.kill()

import os 
os.remove("my_conn_conf.json")
```

```python
# You can use the appropriate conn conf class, 
#   which can offer some benefits such as intellisense in Jupyter or other IDE.
# The below will use an Oracle Connection Configuration Class

from practicuscore.api_base import OracleConnConf, PRTValidator

oracle_conn_conf = OracleConnConf(
    db_host="my.orcle.db.address",
    service_name="my_service",
    sid="my_sid",
    user="alice",
    password="in-wonderland",
    sql_query="select * from my_table",

    # Wrong port !!
    db_port=100_000,
)

# We deliberately entered the wrong Oracle port. Let's validate, and fail
field_name, issue = PRTValidator.validate(oracle_conn_conf)
if issue:
    print(f"'{field_name}' field has an issue: {issue}")
# Will print:
# 'db_port' field has an issue: Port must be between 1 and 65,535

# With the right Oracle db connection info, you would be able to load
# proc = worker.load(oracle_conn_conf)
# df = proc.get_df_copy()
```

```python
# Practicus AI conn conf objects are easy to convert to a dictionary
print("Oracle conn dict:", oracle_conn_conf.model_dump())
```

```python
# Or to json
oracle_conn_conf_json = oracle_conn_conf.to_json()
print("Oracle conn json:", oracle_conn_conf_json)
```

```python
# And, vice versa. from a dict or json back to class the instance
# This can be very conventient, e.g. save to a file, including the SQL Query, 
# and reuse later, e.g. scheduled every night in Airflow.
reloaded_oracle_conn_conf = OracleConnConf.from_json(oracle_conn_conf_json)
type(reloaded_oracle_conn_conf)
```

#### Loading using the Data Catalog

When you read a connection from Practicus AI Data Catalog, you also download it's "base" connection configuration class.

But instead of the database credentials like user name, password etc. you will load a "reference" (uuid) to the Data Catalog. 

Practicus AI workers will load data intelligently; 
- if there are database credentials in the conn conf, these will be used.
- Or else, the worker will sue your credentials to "fetch" connection credentials from the Data Catalog, and by using the reference.

```python
# Accessing the conn_conf will print the json
conn_conf_object = first_connection.conn_conf
conn_conf_object
```

In most cases, accesing the "conn_conf" of a connection that you load from the Data Catalog will just have:

- Connection type, e.g. Oracle
- And the unique reference uuid
  
For relational DBs, you can just supply a SQL query and you're good to go. Practicus AI will take care of the rest.

```python
# The conn_conf is actually a child class of ConnConf
type(conn_conf_object)
# e.g. OracleConnconf
```

```python
# Let's make sure we use a connection type that can run a SQL statement, 
#   which will be a child class of Relational DB class RelationalConnConf. 
from practicuscore.api_base import RelationalConnConf

if not isinstance(conn_conf_object, RelationalConnConf):
    raise ConnectionError("The rest of the notebook needs a conn type that can run SQL")
```

```python
# With the below code, you can see that the conn conf class has many advanced properties
# dir(conn_conf_object)
# We just need to use sql_query property
conn_conf_object.sql_query = "Select * from Table"
```

```python
# In additon to a dict, json or json file, we can also use a conn conf object to read data
# proc = worker.load(conn_conf_object)
```

#### Summary

Let's summarize some of the common options to load data.

```python
region = prt.current_region()

print("My connections:", region.connection_list)

postgres_conn = region.get_connection("My Team/My Postgres")
if postgres_conn:
    postgres_conn.sql_query = "Select * from Table"
    proc = worker.load(postgres_conn)

redshift_conn = region.get_connection("Some Department/Some Project/Some Redshift")
if redshift_conn:
    conn_dict = redshift_conn.model_dump()
    conn_dict["sql_query"] = "Select * from Table"
    proc = worker.load(redshift_conn)

conn_with_credentials = {
    "connection_type": "SNOWFLAKE",
    "db_name": "my.snowflake.com",
    # add warehouse etc. 
    "user": "bob",
    "password": "super-secret",
    "sql_query": "Select * from Table"
}
# proc = worker.load(conn_with_credentials)

# And lastly, which can include all the DB credentials + SQL
#  or a reference to the data catalog + SQL
# proc = worker.load("path/to/my_conn.json")
```

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
