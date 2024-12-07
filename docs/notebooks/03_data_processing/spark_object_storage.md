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
# For AWS S3
connection = {
    "connection_type": "S3",
    "aws_region": "us-east-1",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    # Optional
    # "aws_session_token", "..."
}
```

```python
# For others, e.g. Minio
connection = {
    "connection_type": "S3",
    "endpoint_url": "http://prt-svc-sampleobj.prt-ns.svc.cluster.local",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
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