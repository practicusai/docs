# Data Lakehouse Integration with Trino, Nessie, MinIO, and Spark

This document outlines the setup and functionalities of a data lakehouse environment leveraging Trino, Nessie, MinIO, and Spark on Practicus. It covers Trino catalog configurations, Kerberos authentication for Spark, and various Spark operations for interacting with HDFS, Hive, and Nessie-managed Iceberg tables.

## Trino Configuration

The Trino deployment is configured with `lakehouse` and `oracle` catalogs to connect to different data sources. The `lakehouse` catalog, whose name is derived directly from the Trino YAML configuration, facilitates interaction with Iceberg tables managed by Nessie, storing data on MinIO. The `oracle` catalog enables direct queries against an Oracle database.

```yaml
additionalCatalogs:
  lakehouse: |-
    connector.name=iceberg
    iceberg.catalog.type=nessie
    iceberg.file-format=PARQUET
    iceberg.unique-table-location=true
    fs.hadoop.enabled=false
    fs.native-s3.enabled=true
    s3.path-style-access=true
    s3.endpoint=${ENV:S3_ENDPOINT}
    s3.aws-access-key=${ENV:S3_ACCESS_KEY_ID}
    s3.aws-secret-key=${ENV:S3_SECRET_ACCESS_KEY}
    s3.region=${ENV:AWS_REGION}
    iceberg.nessie-catalog.uri=${ENV:NESSIE_URI}
    iceberg.nessie-catalog.default-warehouse-dir=s3a://{<MINIO_BUCKET_NAME>}
  oracle: |-
    connector.name=oracle
    connection-url=jdbc:oracle:thin:@{<ORACLE_SERVER_IP>}:{<ORACLE_PORT>}/{<ORACLE_SERVICE_NAME>}
    connection-user={ <ORACLE_USER> }
    connection-password={ <ORACLE_PASSWORD> }
```

* `lakehouse` Catalog:
    * `connector.name=iceberg`: Specifies the Iceberg connector.
    * `iceberg.catalog.type=nessie`: Configures Nessie as the Iceberg catalog.
    * `iceberg.file-format=PARQUET`: Sets the default file format for Iceberg tables to Parquet.
    * `s3.endpoint`, `s3.aws-access-key`, `s3.aws-secret-key`: These environment variables are used to connect to the MinIO object storage.
    * `iceberg.nessie-catalog.uri`: Points to the Nessie service URI.
    * `iceberg.nessie-catalog.default-warehouse-dir`: Defines the default storage location for Iceberg tables in MinIO.

* `oracle` Catalog:
    * **`connector.name=oracle`**: Specifies the Oracle connector.
    * **`connection-url`**: The JDBC URL to connect to the Oracle database.
    * **`connection-user`** and **`connection-password`**: Credentials for database access.

## Spark Setup with Kerberos Authentication

The Spark environment is configured to interact with HDFS and Hive, utilizing Kerberos for secure authentication. This setup involves embedding Kerberos tickets within the Spark image and configuring Hadoop/Hive properties. The Spark version deployed is **3.5.3**. Compatible Nessie and Iceberg libraries have been added to the Spark image and are made available to Spark sessions.

### Compatible Libraries for Spark 3.5.3

The following libraries are included in the Spark image under `/opt/spark/jars/` to ensure compatibility with Spark 3.5.3, Iceberg, and Nessie:

* `aws-java-sdk-bundle-1.12.262.jar`
* `hadoop-aws-3.3.4.jar`
* `iceberg-spark-runtime-3.5_2.12-1.5.0.jar`
* `nessie-spark-extensions-3.5_2.12-0.104.1.jar`

These JARs are specified in the `spark.driver.extraClassPath` and `spark.executor.extraClassPath` options during Spark session initialization.

### Kerberos Ticket Generation (within image)

The Spark image includes scripts to generate Kerberos tickets using `ktutil` and `kinit`. This process ensures that Spark applications can securely access Kerberized services like HDFS.

```bash
!ktutil
addent -password -p {<user_name>}@{<REALM_NAME>} -k 1 -e aes256-cts
{<password>}
wkt /home/ubuntu/{<user_name>}.keytab
q
!kinit -kt /home/ubuntu/{<user_name>}.keytab {<user_name>}@{<REALM_NAME>} -l 12h
!klist
```

* `ktutil`: Utility for managing Kerberos keytabs.
    * `addent`: Adds an entry to the keytab.
    * `wkt`: Writes the keytab to a file.
* `kinit`: Obtains and caches a Kerberos ticket-granting ticket.
    * `-kt`: Specifies the keytab file for authentication.
    * `-l`: Specifies the lifetime of the ticket.

### Spark Session Initialization

The following Python code demonstrates how a Spark session is initialized with necessary configurations for Iceberg, Nessie, S3 (MinIO), HDFS, and Hive integration, along with Kerberos-related environment variables.

```python
import os
from pyspark.sql import SparkSession

# Set environment variables for Hadoop, Spark, Hive, and Kerberos configurations
os.environ['HADOOP_CONF_DIR'] = "/home/ubuntu/{<config_directory>}/" # Path to core-site.xml, hdfs-site.xml, etc.
os.environ['SPARK_CONF_DIR'] = "/home/ubuntu/{<config_directory>}/"
os.environ['HIVE_CONF_DIR'] = "/home/ubuntu/{<config_directory>}/"
os.environ['KRB5_CONFIG'] = "/etc/krb5.conf" # Path to Kerberos configuration file
os.environ['KRB5CCNAME'] = "/tmp/krb5cc_1000" # Kerberos credential cache file

spark = SparkSession.builder \
    .appName("IcebergNessieIntegration") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.lakehouse.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog") \
    .config("spark.sql.catalog.lakehouse.uri", "{<Nessie_URI>}") \
    .config("spark.sql.catalog.lakehouse.ref", "main") \
    .config("spark.sql.catalog.lakehouse.warehouse", "s3a://{<MINIO_BUCKET_NAME>}") \
    .config("spark.hadoop.fs.s3a.endpoint", "{<MinIO_URI>}") \
    .config("spark.hadoop.fs.s3a.access.key", "{<S3_ACCESS_KEY>}") \
    .config("spark.hadoop.fs.s3a.secret.key", "{<S3_SECRET_KEY>}") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.driver.extraClassPath", "/opt/spark/jars/*") \
    .config("spark.executor.extraClassPath", "/opt/spark/jars/*") \
    .enableHiveSupport() \
    .getOrCreate()
```

* Environment Variables: Set paths for Hadoop, Spark, Hive, and Kerberos configuration files.
* Spark Configurations:
    * `spark.sql.extensions`: Enables Iceberg Spark extensions.
    * `spark.sql.catalog.lakehouse`: Configures the `lakehouse` catalog for Iceberg and Nessie.
    * `spark.hadoop.fs.s3a.endpoint`, `spark.hadoop.fs.s3a.access.key`, `spark.hadoop.fs.s3a.secret.key`: MinIO (S3-compatible) connection details.
    * `spark.driver.extraClassPath` and `spark.executor.extraClassPath`: These point to `/opt/spark/jars/*`, ensuring that the compatible `aws-java-sdk-bundle`, `hadoop-aws`, `iceberg-spark-runtime`, and `nessie-spark-extensions` JARs are available to Spark.
    * `enableHiveSupport()`: Integrates Spark with Hive.

## Spark Operations

This section demonstrates various Spark operations, including reading data from HDFS, querying Hive, and interacting with Iceberg tables managed by Nessie.

### Reading Data from HDFS

Spark can directly read data from HDFS locations, leveraging the Kerberos authentication configured in the Spark environment.

#### Reading a Specific File from HDFS

```python
df = spark.read.format("parquet") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("hdfs://<namenode>/warehouse/tablespace/external/hive/<schema_name>/<table_name>/year=2024/month=12/day=4/part-00000-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-c000")

print(f"DataFrame loaded from HDFS. Row count: {df.count()}")
df.printSchema()
```

This code snippet reads a single Parquet file from a specified HDFS path.

#### Reading and Consolidating Multiple Files from HDFS Folder

```python
import pandas as pd

folder_path_for_listing = "hdfs://<namenode>/warehouse/tablespace/external/hive/<schema_name>/<table_name>/year=2024/month=12/day=4/"

try:
    df_from_folder = spark.read.format("parquet") \
                                .option("header", "true") \
                                .option("inferSchema", "true") \
                                .load(f"{folder_path_for_listing}*")

    print(f"Type of df_from_folder variable: {type(df_from_folder)}")
    
    pandas_df_first_10 = df_from_folder.limit(10).toPandas()

    print(pandas_df_first_10)

except Exception as e:
    print(f"An error occurred: {e}")
```

This script reads all Parquet files within a given HDFS directory, consolidates them into a single DataFrame, and then displays the first 10 rows as a Pandas DataFrame.

### Interacting with Hive

Spark, with `enableHiveSupport()`, can list databases and tables stored in Hive Metastore.

#### Listing Databases in Hive

```python
spark.sql("SHOW DATABASES;").show()
```

This command displays all databases accessible via the configured Hive Metastore.

#### Listing Tables in a Specific Hive Database

```python
spark.sql("SHOW TABLES IN <hive_schema_name>").show()
```

This command lists all tables within the `<hive_schema_name>` database in Hive.

#### Querying a Table in Hive

```python
df = spark.sql("select * from <hive_schema_name>.<hive_table_name> limit 50")
df.toPandas()
```

This retrieves the first 50 rows from the `<hive_table_name>` table in the `<hive_schema_name>` database and converts them into a Pandas DataFrame.

### Interacting with Nessie-Managed Iceberg Tables

Spark's integration with Iceberg and Nessie allows for powerful data lake operations, including listing tables, querying, appending, creating, and managing Iceberg tables.

#### Listing Tables in Nessie Catalog

```python
spark.sql("SHOW TABLES IN lakehouse.<nessie_namespace_name>").show()
```

This command lists all tables within the `<nessie_namespace_name>` of the `lakehouse` catalog (Nessie).

#### Counting Records in an Iceberg Table

```python
spark.sql("SELECT COUNT(*) FROM lakehouse.<nessie_namespace_name>.<iceberg_table_name_1>").show()
```

This query counts the total number of records in the `<iceberg_table_name_1>` table, which is managed by Nessie.

#### Appending Data to an Iceberg Table

```python
df.writeTo("lakehouse.<nessie_namespace_name>.<iceberg_table_name_1>").append()
spark.sql("SELECT COUNT(*) FROM lakehouse.<nessie_namespace_name>.<iceberg_table_name_1>").show()
```

This appends the contents of the `df` DataFrame to the `<iceberg_table_name_1>` Iceberg table. After appending, it recounts the records to show the updated count.

#### Creating a New Iceberg Table

```python
df.writeTo("lakehouse.<nessie_namespace_name>.<iceberg_table_name_2>").create()
spark.sql("SHOW TABLES IN lakehouse.<nessie_namespace_name>").show()
```

This creates a new Iceberg table named `<iceberg_table_name_2>` in the `lakehouse.<nessie_namespace_name>` namespace using the schema and data from `df`. It then lists the tables to confirm its creation.

#### Querying an Iceberg Table

```python
spark.sql("SELECT * FROM lakehouse.<nessie_namespace_name>.<iceberg_table_name_1>").show()
```

This displays all records from the `<iceberg_table_name_1>` Iceberg table.

#### Creating an Empty Iceberg Table with a Defined Schema

```python
spark.sql("CREATE TABLE lakehouse.<nessie_namespace_name>.<iceberg_table_name_3> (column1 STRING, column2 STRING, column3 STRING, column4 STRING, column5 STRING)")
spark.sql("SHOW TABLES IN lakehouse.<nessie_namespace_name>").show()
```

This command creates an empty Iceberg table named `<iceberg_table_name_3>` with a predefined schema in the `lakehouse.<nessie_namespace_name>` namespace. The tables are then listed to confirm its creation.

### Stopping the Spark Session

```python
spark.stop()
```

This command terminates the Spark session, releasing all associated resources.