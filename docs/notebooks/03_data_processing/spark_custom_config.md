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
s3_access = ""
s3_secret = ""

# For AWS S3 
s3_endpoint = "s3.amazonaws.com"
# For others, e.g. Minio
# s3_endpoint = "http://prt-svc-sampleobj.prt-ns.svc.cluster.local"
```

```python
extra_spark_conf = {
    "spark.hadoop.fs.s3a.path.style.access": "true",
    "spark.hadoop.fs.s3a.access.key" : s3_access,
    "spark.hadoop.fs.s3a.secret.key" : s3_secret,
    "spark.hadoop.fs.s3a.endpoint": s3_endpoint
}

import practicuscore as prt 

spark = prt.engines.get_spark_session(extra_spark_conf=extra_spark_conf)

df = spark.read.csv("s3a://sample-bucket/boston.csv")
df.head()
```
