---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Executing batch jobs in Spark Cluster

In this example we will:
- Create a Spark cluster
- Submit a job python file
- Terminate the cluster after job is completed.

### Before you begin
- Create "spark" under your "~/my" folder
- And copy job.py under this (spark_with_job) folder

```python
worker_size = None
worker_count = None
log_level = "DEBUG"
```

```python
assert worker_size, "Please enter your worker_size."
assert worker_count, "Please enter your worker_count."
assert log_level, "Please enter your log_level."
```

```python
import practicuscore as prt

job_dir = "~/my/spark_with_job/"


distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.spark,
    job_dir=job_dir,
    py_file="job.py",
    worker_count=worker_count,
    terminate_on_completion=False,
)

worker_config = prt.WorkerConfig(worker_size=worker_size, distributed_config=distributed_config, log_level=log_level)

coordinator_worker = prt.create_worker(
    worker_config=worker_config,
)
```

```python
prt.distributed.live_view(
    job_dir=job_dir,
    job_id=coordinator_worker.job_id,
)
```

```python
# You can view the logs during or after the job is completed
# To view coordinator (master) set rank = 0
rank = 0
# To view other workers set rank = 1,2, ..

prt.distributed.view_log(job_dir=job_dir, job_id=coordinator_worker.job_id, rank=rank)
```


## Supplementary Files

### job.py
```python
import practicuscore as prt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit, max, min, stddev, corr
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml import Pipeline

spark = SparkSession.builder.appName("Advanced Data Processing").getOrCreate()

file_path = "/home/ubuntu/samples/data/insurance.csv"
data = spark.read.csv(file_path, header=True, inferSchema=True)
missing_data = data.select([count(when(col(c).isNull(), c)).alias(c) for c in data.columns])

categorical_columns = ["sex", "smoker", "region"]
indexers = [StringIndexer(inputCol=col, outputCol=col + "_index") for col in categorical_columns]
encoders = [OneHotEncoder(inputCol=col + "_index", outputCol=col + "_encoded") for col in categorical_columns]

data = data.withColumn(
    "bmi_category",
    when(col("bmi") < 18.5, lit("underweight"))
    .when((col("bmi") >= 18.5) & (col("bmi") < 25), lit("normal"))
    .when((col("bmi") >= 25) & (col("bmi") < 30), lit("overweight"))
    .otherwise(lit("obese")),
)

feature_columns = ["age", "bmi", "children", "sex_encoded", "smoker_encoded", "region_encoded"]
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=False)

pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler])
data = pipeline.fit(data).transform(data)

output_path = "/home/ubuntu/my/processed_insurance_data.parquet/"

data.write.parquet(output_path, mode="overwrite")

spark.stop()

```

### run/2c741e/prt_dist_job.json
```json
{"job_type":"spark","job_dir":"~/my/02_batch_job/","initial_count":2,"coordinator_port":7077,"additional_ports":[4040,7078,7079],"terminate_on_completion":false,"py_file":"job.py","executors":[{"rank":0,"instance_id":"5cf16b71"},{"rank":1,"instance_id":"63e80dc8"}]}
```

### run/2c741e/rank_0.json
```json
{"rank":0,"instance_id":"5cf16b71","state":"completed","used_ram":1187,"peak_ram":1187,"total_ram":3200,"gpus":0,"used_vram":0,"peak_vram":0,"reserved_vram":0,"total_vram":0}
```

### run/2c741e/rank_1.json
```json
{"rank":1,"instance_id":"63e80dc8","state":"running","used_ram":284,"peak_ram":293,"total_ram":3200,"gpus":0,"used_vram":0,"peak_vram":0,"reserved_vram":0,"total_vram":0}
```


---

**Previous**: [Spark Tutorial](../spark-for-ds/spark-tutorial.md) | **Next**: [XGBoost > XGBoost](../../xgboost/xgboost.md)
