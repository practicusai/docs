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

# Practicus AI Data Catalog

Practicus AI provides a Data Catalog where you, or an administrator can save data source connection information. 

Data sources can be Data Lakes, Object Storage (E.g. S3), Data Warehouses (E.g. Snowflake), Databases (e.g. Oracle) ...

Data catalog info does **not** include details like the actual SQL queries to run, S3 keys to read etc., but just the info such as host address, port (if needed), user name, password etc. You can think of them as a "connection string" in most programming languages. 

```python
import practicuscore as prt

# Connections are saved under a Practicus AI region
region = prt.current_region()

# You can also connect to a remote region instead of the default one
# region = prt.regions.get_region(..)
```

```python
# Let's get connections that we have access to
# If a connection is missing, please ask your admin to be granted access,
# OR, create new connections using the Practicus AI App or SDK
connections = region.connection_list

if len(connections) == 0:
    raise ConnectionError("You or an admin has not defined any connections yet. This notebook will not be meaningful..")
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
        raise ConnectionError("Please run this code on a Practicus AI worker, or have at least one active worker")
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
    "file_path": "/home/ubuntu/samples/data/chinook.db",
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
    db_host="my.oracle.db.address",
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
oracle_conn_conf_json = oracle_conn_conf.model_dump_json()
print("Oracle conn json:", oracle_conn_conf_json)
```

```python
# And, vice versa. from a dict or json back to class the instance
# This can be very convenient, e.g. save to a file, including the SQL Query,
# and reuse later, e.g. scheduled every night in Airflow.
reloaded_oracle_conn_conf = OracleConnConf.model_validate_json(oracle_conn_conf_json)
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

In most cases, accessing the "conn_conf" of a connection that you load from the Data Catalog will just have:

- Connection type, e.g. Oracle
- And the unique reference uuid
  
For relational DBs, you can just supply a SQL query and you're good to go. Practicus AI will take care of the rest.

```python
# The conn_conf is actually a child class of ConnConf
type(conn_conf_object)
# e.g. OracleConnConf
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
# In addition to a dict, json or json file, we can also use a conn conf object to read data
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
    "sql_query": "Select * from Table",
}
# proc = worker.load(conn_with_credentials)

# And lastly, which can include all the DB credentials + SQL
#  or a reference to the data catalog + SQL
# proc = worker.load("path/to/my_conn.json")
```


---

**Previous**: [Work With Processes](work-with-processes.md) | **Next**: [Caching Large Model Files](caching-large-model-files.md)
