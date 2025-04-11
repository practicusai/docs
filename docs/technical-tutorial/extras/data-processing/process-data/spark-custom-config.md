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

```python
# Defining Parameters
s3_access = None
s3_secret = None
s3_bucket_uri = None  # E.g "s3a://sample-bucket/boston.csv"
```

```python
assert s3_access, "Please enter an access key"
assert s3_secret, "Please enter an secret key"
assert s3_bucket_uri, "Please enter s3 bucket uri"
```

```python
# For AWS S3
s3_endpoint = "s3.amazonaws.com"
# For others, e.g. Minio
# s3_endpoint = "http://prt-svc-sampleobj.prt-ns.svc.cluster.local"
```

```python
extra_spark_conf = {
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.access.key": s3_access,
    "spark.hadoop.fs.s3a.secret.key": s3_secret,
    "spark.hadoop.fs.s3a.endpoint": s3_endpoint,
}

import practicuscore as prt

spark = prt.engines.get_spark_session(extra_spark_conf=extra_spark_conf)

df = spark.read.csv(s3_bucket_uri)
df.head()
```


---

**Previous**: [Insurance With Remote Worker](insurance-with-remote-worker.md) | **Next**: [Spark Object Storage](spark-object-storage.md)
