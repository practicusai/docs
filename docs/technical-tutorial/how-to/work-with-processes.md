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

# Practicus AI Processes

Practicus AI Processes live in Practicus AI Workers and you can create, work with and kill them as the below.

```python
import practicuscore as prt
```

```python
worker = prt.get_local_worker()
```

```python
# We can also create a remote worker by running the below, either from your computer,
# or from an existing Practicus AI worker.
worker_config = {
    "worker_size": "Small",
    "worker_image": "practicus",
}
# worker = prt.create_worker(worker_config) 
```

```python
# Processes start by loading some data.  
worker_file_conn = {
    "connection_type": "WORKER_FILE",
    "file_path": "/home/ubuntu/samples/ice_cream.csv"
}

proc_1 = worker.load(worker_file_conn)
proc_1.show_head()
```

```python
# Let's create another process
sqlite_conn = {
    "connection_type": "SQLITE",
    "file_path": "/home/ubuntu/samples/chinook.db",
    "sql_query": "select * from artists"
}

proc_2 = worker.load(sqlite_conn)
proc_2.show_head()
```

```python
# Let's iterate over processes
for proc in worker.proc_list:
    print(f"Process id: {proc.proc_id} connection: {proc.conn_info}")
```

```python
# Converting the proc_list into string will give you a csv 
print(worker.proc_list)
```

```python
# You can also get current processes as a pandas DataFrame for convenience
worker.proc_list.to_pandas()
```

```python
# Simply accessing the proc_list will also print a formatted table string 
worker.proc_list
```

```python
first_proc = worker.proc_list[0]
# Accessing a process object will print it's details
first_proc
```

```python
# You can ask a process to kill itself and free resources
proc_1.kill()
```

```python
# It's parent worker will be updated
worker.proc_list.to_pandas()
```

```python
# You can also ask a worker to kill one of it's processes
remaining_proc_id = worker.proc_list[0].proc_id
worker.kill_proc(remaining_proc_id)
```

```python
# Will return empty
worker.proc_list.to_pandas()
```

```python
# You can also ask a worker to kill all its processes to free up resources faster
worker.kill_all_procs()
```


---

**Previous**: [Use Security Tokens](use-security-tokens.md) | **Next**: [Work With Data Catalog](work-with-data-catalog.md)
