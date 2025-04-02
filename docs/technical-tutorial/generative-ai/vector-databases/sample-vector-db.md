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

<!-- #region -->
# Milvus vector database sample

This example demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.


## Before you begin

Please make sure that you have a running Milvus instance.


<!-- #endregion -->

```python
milvus_host = None
milvus_port = None
```

```python
assert milvus_host, "Please enter your Milvus connection uri."
assert milvus_port, "Please enter your Milvus port."
```

## Steps 

1. connect to Milvus
2. create collection
3. insert data
4. create index
5. search, query, and hybrid search on entities
6. delete entities by PK
7. drop collection

```python
import numpy as np
import time

from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"
num_entities, dim = 3000, 8
```

## 1. connect to Milvus

Add a new connection alias `default` for Milvus server in `localhost:19530`. 

Actually the `default` alias is a building in PyMilvus. If the address of Milvus is the same as `localhost:19530`, you can omit all parameters and call the method as: `connections.connect()`.

Note: the `using` parameter of the following methods is default to "default".

```python
connections.connect("default", host=milvus_host, port=milvus_port)

has = utility.has_collection("hello_milvus")
print(f"Does collection hello_milvus exist in Milvus: {has}")
```

## 2. create collection
We're going to create a collection with 3 fields.

|   |field name  |field type |other attributes              |  field description      |
|---|:----------:|:---------:|:----------------------------:|:-----------------------:|
|1  |    "pk"    |   VARCHAR |is_primary=True, auto_id=False|      "primary field"    |
|2  |  "random"  |   Double  |                              |      "a double field"   |
|3  |"embeddings"|FloatVector|     dim=8                    |"float vector with dim 8"|

```python
fields = [
    FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=100),
    FieldSchema(name="random", dtype=DataType.DOUBLE),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dim)
]

schema = CollectionSchema(fields, "hello_milvus is the simplest demo to introduce the APIs")

hello_milvus = Collection("hello_milvus", schema, consistency_level="Strong")
```

## 3. insert data

We are going to insert 3000 rows of data into `hello_milvus`. Data to be inserted must be organized in fields.

The insert() method returns:
- either automatically generated primary keys by Milvus if auto_id=True in the schema;
- or the existing primary key field from the entities if auto_id=False in the schema.

```python
rng = np.random.default_rng(seed=19530)
entities = [
    # provide the pk field because `auto_id` is set to False
    [str(i) for i in range(num_entities)],
    rng.random(num_entities).tolist(),  # field random, only supports list
    rng.random((num_entities, dim)),    # field embeddings, supports numpy.ndarray and list
]

insert_result = hello_milvus.insert(entities)

print(f"Number of entities in Milvus: {hello_milvus.num_entities}")  # check the num_entites
```

## 4. create index
We are going to create an IVF_FLAT index for hello_milvus collection.

create_index() can only be applied to `FloatVector` and `BinaryVector` fields.

```python
index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}

hello_milvus.create_index("embeddings", index)
```

## 5. search, query, and hybrid search
After data were inserted into Milvus and indexed, you can perform:
- search based on vector similarity
- query based on scalar filtering(boolean, int, etc.)
- hybrid search based on vector similarity and scalar filtering.

Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.

```python
hello_milvus.load()
```

**Search based on vector similarity**

```python
vectors_to_search = entities[-1][-2:]
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10},
}

start_time = time.time()
result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, output_fields=["random"])
end_time = time.time()

for hits in result:
    for hit in hits:
        print(f"hit: {hit}, random field: {hit.entity.get('random')}")
print(search_latency_fmt.format(end_time - start_time))
```

**Query based on scalar filtering(boolean, int, etc.)**

Start querying with `random > 0.5`

```python
start_time = time.time()
result = hello_milvus.query(expr="random > 0.5", output_fields=["random", "embeddings"])
end_time = time.time()

print(f"query result:\n-{result[0]}")
print(search_latency_fmt.format(end_time - start_time))
```

**Hybrid search**

Start hybrid searching with `random > 0.5`

```python
start_time = time.time()
result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, expr="random > 0.5", output_fields=["random"])
end_time = time.time()

for hits in result:
    for hit in hits:
        print(f"hit: {hit}, random field: {hit.entity.get('random')}")
print(search_latency_fmt.format(end_time - start_time))
```

## 6. delete entities by PK
You can delete entities by their PK values using boolean expressions.


```python
ids = insert_result.primary_keys
expr = f'pk in ["{ids[0]}", "{ids[1]}"]'

result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
print(f"query before delete by expr=`{expr}` -> result: \n-{result[0]}\n-{result[1]}\n")

hello_milvus.delete(expr)

result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
print(f"query after delete by expr=`{expr}` -> result: {result}\n")
```

## 7. drop collection
Finally, drop the hello_milvus collection

```python
utility.drop_collection("hello_milvus")
```


---

**Previous**: [Embeddings](../langchain/embeddings.md) | **Next**: [OpenAI Compatibility > Models > Build](../openai-compatibility/models/build.md)
