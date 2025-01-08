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

```python
# Defining Parameters
aws_region = None
aws_access_key_id = None
aws_secret_access_key= None
endpoint_url = None # example "http://prt-svc-sampleobj.prt-ns.svc.cluster.local",

```

```python
assert aws_region, "Please enter a aws_region"
assert aws_access_key_id, "Please enter a aws_access_key_id"
assert aws_secret_access_key, "Please enter a aws_secret_access_key"
assert endpoint_url, "Please enter a endpoint_url"
```

```python
# For AWS S3
connection = {
    "connection_type": "S3",
    "aws_region": aws_region,
    "aws_access_key_id": aws_access_key_id,
    "aws_secret_access_key":aws_secret_access_key,
    # Optional
    # "aws_session_token", "..."
}
```

```python
# For others, e.g. Minio
connection = {
    "connection_type": "S3",
    "endpoint_url": endpoint_url, 
    "aws_access_key_id": aws_access_key_id,
    "aws_secret_access_key": aws_secret_access_key,
}
```

```python
import practicuscore as prt 

# Create a Spark session
spark = prt.engines.get_spark_session(connection)

# If you are using distributed Spark, you should now have the Spark cluster up & running. 
```

```python
df = spark.read.csv("s3a://sample/boston.csv")
df.head()
```

```python
# Optional: delete Spark Session 
prt.engines.delete_spark_session(spark)

# If you are using distributed Spark, you should now have the Spark cluster terminated.
# You can also terminate your worker, which will automatically terminate the child Spark Cluster. 
```


---

**Previous**: [Spark Custom Config](spark-custom-config.md) | **Next**: [Modeling > SparkML > SparkML Ice Cream](../../modeling/sparkml/sparkml-ice-cream.md)
