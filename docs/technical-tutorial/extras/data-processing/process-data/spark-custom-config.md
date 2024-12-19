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

This code configures the necessary settings to connect to an S3 service. It includes the following steps:

1. **Access Keys**:
   - `s3_access` and `s3_secret` variables define the access key and secret key used to connect to AWS S3 or another S3-compatible service. These values are currently left empty.

2. **S3 Endpoint**:
   - `s3_endpoint = "s3.amazonaws.com"`: The default endpoint for AWS S3 is specified here, which connects to the Amazon S3 service.

3. **Alternative Endpoint (Commented Out)**:
   - `# s3_endpoint = "http://prt-svc-sampleobj.prt-ns.svc.cluster.local"`: This line specifies an alternative endpoint for another S3-compatible service (e.g., Minio). However, it is currently commented out and not active.


```python
s3_access = ""
s3_secret = ""

# For AWS S3 
s3_endpoint = "s3.amazonaws.com"
# For others, e.g. Minio
# s3_endpoint = "http://prt-svc-sampleobj.prt-ns.svc.cluster.local"
```

## Spark Session Setup and S3 File Reading

### **Purpose**
This code sets up a Spark session to read a CSV file from an S3 bucket using the `spark.read.csv()` method. It configures Spark to use the S3 file system with the provided access credentials and endpoint.

### **Details**
1. **Extra Spark Configuration (`extra_spark_conf`)**:
   - This dictionary defines additional configuration settings for Spark to work with S3:
     - `"spark.hadoop.fs.s3a.path.style.access": "true"`: This enables path-style access for S3, which is necessary for some S3-compatible storage services.
     - `"spark.hadoop.fs.s3a.access.key": s3_access`: The access key to authenticate with the S3 service.
     - `"spark.hadoop.fs.s3a.secret.key": s3_secret`: The secret key associated with the access key.
     - `"spark.hadoop.fs.s3a.endpoint": s3_endpoint`: Specifies the endpoint to use when accessing the S3 service.

2. **Importing `practicuscore` and Spark Session**:
   - `import practicuscore as prt`: The code imports the `practicuscore` library, which is used to interact with the Spark engine.
   - `spark = prt.engines.get_spark_session(extra_spark_conf=extra_spark_conf)`: This line retrieves a Spark session using the configurations defined earlier. It includes the S3 credentials and endpoint settings.

3. **Reading the CSV File**:
   - `df = spark.read.csv("s3a://sample-bucket/boston.csv")`: This reads the CSV file from the specified S3 bucket (`sample-bucket`) into a Spark DataFrame (`df`).
   - `"s3a://"`: The protocol used to read from S3-compatible storage.

4. **Displaying the First Few Rows**:
   - `df.head()`: Displays the first few rows of the DataFrame `df` to check the data.


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


---

**Previous**: [Insurance With Remote Worker](insurance-with-remote-worker.md) | **Next**: [Spark Object Storage](spark-object-storage.md)
