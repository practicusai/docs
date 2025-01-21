---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

## Insurance Sample SDK Usage with *Remote Worker*
### _Scenario:_ Process on the Notebook

1. _Open_ *Jupyter Notebook*
    
2. Create json for worker and connection.(*Json generation code coming soon*)
   - The Worker json file must contain the following configurations:
   - *Service url, worker_size, worker_image, email, and refresh_token*
  
   - The Connection json file must contain the following configurations:
   - *Connection_type, ws_uuid, ws_name, and file_path*
  
3. Encoding *categorical variables*
    
4. Delete the originals of the columns you *encoded*

5. Run the process and *kill* processing when finished


Create a new worker with practicuscore method of "create_worker" and use this new worker for your operations

```python
worker_conf = {
    "worker_size": "Medium",
    "worker_image": "practicus",
    #"service_url": "",
    #"email": "",
    #"refresh_token": "**entry_your_token**"
}
```

```python
import practicuscore as prt

worker = prt.create_worker(worker_conf)
```

- To access the dataset you need to work with connection configuration dictionary
- Also, you can choose a different Engine than Advance in the Deploy phase

```python
# configuration of connection

data_set_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/insurance.csv"
}
```

```python
proc = worker.load(data_set_conn, engine='AUTO') 
```

Data prep with Practicus ai SDK

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
proc.wait_until_done(timeout_min=600)
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

```python
worker.terminate()
```

### You can also prepare this code directly in pipeline:
##### If you make the process functional and do it with with, you don't need to kill the worker when the process is finished. The worker is automatically killed when this process is finished

```python
with prt.create_worker(worker_conf) as worker: 
    with worker.load(data_set_conn) as proc:
        proc.categorical_map(column_name='sex', column_suffix='category'), 
        proc.categorical_map(column_name='smoker', column_suffix='category'),
        proc.categorical_map(column_name='region', column_suffix='category'),
        proc.delete_columns(['region', 'smoker', 'sex']) 
        proc.wait_until_done(timeout_min=600)
        proc.show_logs()
```


---

**Previous**: [Insurance](insurance.md) | **Next**: [Spark Custom Config](spark-custom-config.md)
