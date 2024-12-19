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

## AWS S3 Connection Setup

### **Purpose**
This code snippet sets up the connection configuration for accessing AWS S3 using access credentials. It provides the necessary parameters to authenticate and connect to the AWS S3 service.

### **Details**
1. **Connection Type**:
   - `"connection_type": "S3"`: Specifies that the connection type is AWS S3.

2. **AWS Region**:
   - `"aws_region": "us-east-1"`: Defines the AWS region where the S3 bucket is located. In this case, it’s set to the `us-east-1` region.

3. **AWS Access Key**:
   - `"aws_access_key_id": "..."`: The access key ID used to authenticate the connection. This value should be replaced with the actual access key.

4. **AWS Secret Key**:
   - `"aws_secret_access_key": "..."`: The secret access key associated with the access key ID. This value should be replaced with the actual secret key.

5. **Optional Session Token**:
   - `"aws_session_token", "..."`: An optional parameter for session-based authentication when temporary credentials are used. This line is commented out, but can be included if using AWS temporary credentials.

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

## S3 Connection Setup for Other Services (e.g., Minio)

### **Purpose**
This code snippet sets up the connection configuration for accessing an S3-compatible service like Minio. It specifies the necessary parameters for authenticating and connecting to the S3-like service.

### **Details**
1. **Connection Type**:
   - `"connection_type": "S3"`: Specifies that the connection type is S3-compatible, such as Minio or another service.

2. **Endpoint URL**:
   - `"endpoint_url": "http://prt-svc-sampleobj.prt-ns.svc.cluster.local"`: Defines the custom endpoint URL for the S3-compatible service (e.g., Minio). This is different from the default AWS S3 endpoint and points to a local or custom S3-compatible service.

3. **AWS Access Key**:
   - `"aws_access_key_id": "..."`: The access key ID used for authentication with the S3-compatible service. This value should be replaced with the actual access key.

4. **AWS Secret Key**:
   - `"aws_secret_access_key": "..."`: The secret access key associated with the access key ID for authentication. This value should be replaced with the actual secret key.


```python
# For others, e.g. Minio
connection = {
    "connection_type": "S3",
    "endpoint_url": "http://prt-svc-sampleobj.prt-ns.svc.cluster.local",
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
}
```

## Spark Session Creation for Distributed Spark

### **Purpose**
This code snippet creates a Spark session using the `practicuscore` library, which is used for interacting with Spark in a distributed environment.

### **Details**
1. **Importing `practicuscore`**:
   - `import practicuscore as prt`: The `practicuscore` library is imported to access its functions for Spark session creation and other utilities.

2. **Creating a Spark Session**:
   - `spark = prt.engines.get_spark_session(connection)`: This line initializes a Spark session using the connection details passed in the `connection` dictionary. It connects to the specified S3-compatible service or AWS S3, based on the earlier configuration.
   
   - The session is set up with the connection configurations such as `aws_access_key_id`, `aws_secret_access_key`, and the custom `endpoint_url` for S3-compatible services like Minio.

3. **Distributed Spark Cluster**:
   - If you are using a distributed Spark setup, this code will allow you to interact with the Spark cluster, enabling you to process large datasets in parallel across multiple nodes.

```python
import practicuscore as prt 

# Create a Spark session
spark = prt.engines.get_spark_session(connection)

# If you are using distributed Spark, you should now have the Spark cluster up & running. 
```

## Reading a CSV from S3 and Managing Spark Session

### **Purpose**
This code reads a CSV file from an S3 bucket into a Spark DataFrame, displays the first few rows of the DataFrame, and demonstrates how to delete the Spark session when done. Optionally, it also terminates the Spark cluster and worker if using a distributed setup.

### **Details**

1. **Reading the CSV File from S3**:
   - `df = spark.read.csv("s3a://sample/boston.csv")`: This reads the CSV file located in the S3 bucket (`s3a://sample/boston.csv`) into a Spark DataFrame (`df`). The `s3a://` protocol is used to access the file stored in Amazon S3 or compatible services (e.g., Minio).
   
2. **Displaying the First Few Rows**:
   - `df.head()`: Displays the first few rows of the DataFrame (`df`) to inspect the contents of the CSV file loaded from the S3 bucket.

3. **Optional: Deleting the Spark Session**:
   - `prt.engines.delete_spark_session(spark)`: This line deletes the Spark session, which helps in cleaning up resources after finishing the work with Spark.
   
   - This is optional and useful when you no longer need the Spark session, especially in a distributed setup.

4. **Terminating the Spark Cluster and Worker**:
   - If you are using a distributed Spark setup, deleting the Spark session may also terminate the Spark cluster.
   - Optionally, terminating the worker node will automatically terminate the child Spark cluster, freeing up resources.


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
