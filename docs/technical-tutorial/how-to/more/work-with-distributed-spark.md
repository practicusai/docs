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

#### Distributed Spark with Practicus AI 

Practicus AI can create ephemeral Spark clusters. These are disposable, instant use Spark environments with no upper limit on scalability. You can start, use and dispose a Spark cluster within seconds.

A Spark cluster is made up of a Spark Master and one or more Spark Executors. Spark master always run on the primary Practicus AI worker that you start below. Practicus AI worker will then create Spark executors as needed (auto-scales). 

Spark Executors are not Practicus AI Workers, and therefore will have limited installation on them. For additional packages, please create new Practicus AISpark executor docker images and ask Practicus AI Worker to use these images to use for Spark executors.

```python
import practicuscore as prt
```

```python
maximum_spark_executors = 1
# initial executor count is optional since executors auto-scale
# you can set a larger value to speed up autoscaling.
initial_spark_executors = 1

worker_config = {
    "worker_size": "X-Small",
    "worker_image": "practicus",

    # Assign distributed worker settings
    "distributed_conf_dict": {
        "max_count": maximum_spark_executors,
        "initial_count": initial_spark_executors
    },
    
    # To enforce image pull policy to Always, make the below True
    # Only use in dev/test where you cannot easily upgrade image versions
    "k8s_pull_new_image": False,
    # To skip SSL verification
    # Only use in dev/test and for self signed SSL certificates
    "bypass_ssl_verification": False
}
```

```python
# Let's create a Practicus AI worker and let it know we will scale on-demand
worker = prt.create_worker(worker_config)
```

```python
# Let's read from Object stroage. 
# Please note that for distributed Spark you can only read from data sources 
# that the Spark executor also have access to.
connection = {
    "connection_type": "S3",
    "endpoint_url": "http://prt-svc-sampleobj.prt-ns.svc.cluster.local",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
}

spark = prt.engines.get_spark_session(connection)

df = spark.read.csv("s3a://sample/boston.csv")
df.head()
```

```python
# Termianting the worker will terminate Spark executors as well
worker.terminate()
```

```python

```


---

**Previous**: [Work With Data Catalog](work-with-data-catalog.md) | **Next**: [Prepare Data](../../more-examples/advanced-langchain/prepare-data.md)
