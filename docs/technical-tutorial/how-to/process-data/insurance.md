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

## Insurance Sample SDK Usage with *Local Worker*
### _Scenario:_ Process on the interface, deploy and access the process

1. _Open_ *insurance.csv*
    
2. Encoding *categorical variables*

3. Delete the originals of the columns you *encoded*
    
4. Navigating the Deploy button, choosing *Jupyter Notebook* Option:

5. Clicking Advanced and selecting *view code* and *include security token* options:

6. Seeing your *connection* and *worker* json created and your code ready:


Connect to your active worker with get local worker

```python
import practicuscore as prt

worker = prt.get_local_worker()
```

- To access the dataset you need to work with connection configuration dictionary
- Also, you can choose a different Engine than Advance in the Deploy phase

```python
# configuration of connection

data_set_conn = {
    "connection_type": "WORKER_FILE",
    "ws_uuid": "d9b92183-8832-4fd1-8187-ac741ff6aab0",
    "ws_name": "insurance",
    "file_path": "/home/ubuntu/samples/insurance.csv"
}
```

```python
proc = worker.load(data_set_conn) 
```

Data preparation with Practicus AI SDK

```python
proc.categorical_map(column_name='sex', column_suffix='category') 
```

```python
proc.categorical_map(column_name='smoker', column_suffix='category') 
```

```python
proc.categorical_map(column_name='region', column_suffix='category') 
```

```python
proc.delete_columns(['region', 'smoker', 'sex']) 
```

```python
proc.wait_until_done()
proc.show_logs()
```

```python
df = proc.get_df_copy()
display(df)
```

Finish the process

```python
proc.kill()
```

### You can also prepare this code directly in pipeline:
##### If you make the process functional and do it with with, you don't need to kill the worker when the process is finished. The worker is automatically killed when this process is finished

```python
# Running the below will terminate the worker 
# with prt.get_local_worker() as worker:

# E.g. the below would run the task, and then kill the process first, and then the worker.
# with prt.get_local_worker() as worker:
#     with worker.load(data_set_conn) as proc:
#         proc.categorical_map(column_name='sex', column_suffix='category'), 
#         proc.categorical_map(column_name='smoker', column_suffix='category'),
#         proc.categorical_map(column_name='region', column_suffix='category'),
#         proc.delete_columns(['region', 'smoker', 'sex']) 
#         proc.wait_until_done()
#         proc.show_logs()
```


---

**Previous**: [Eda](../explore-data/eda.md) | **Next**: [Insurance With Remote Worker](insurance-with-remote-worker.md)
