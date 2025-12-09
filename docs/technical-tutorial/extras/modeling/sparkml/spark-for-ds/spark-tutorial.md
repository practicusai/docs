---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit, max, min, stddev, corr
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml import Pipeline
```

## SparkSession Creation 

This code creates a `SparkSession` object, which is the entry point for any Spark application. It is used to configure and initialize a Spark application for data processing and analysis.



```python
spark = SparkSession.builder.appName("Advanced Data Processing").getOrCreate()
```

## Reading a CSV File with Spark

A CSV file is loaded into a Spark DataFrame using Spark's `read.csv()` method. This allows the data to be processed and analyzed efficiently within the Spark environment.



```python
file_path = "/home/ubuntu/samples/data/insurance.csv"
data = spark.read.csv(file_path, header=True, inferSchema=True)
```

```python
print("First rows:")
data.show(5)
```

```python
print("Data Schema:")
data.printSchema()
```

## Checking for Null Values in a Spark DataFrame

Null values in a DataFrame are counted for each column, and the results are displayed to assess data completeness.



```python
print("Check Nulls:")
missing_data = data.select([count(when(col(c).isNull(), c)).alias(c) for c in data.columns])
missing_data.show()
```

## Data Summary and Statistical Analysis

Statistical measures such as descriptive statistics, minimum, maximum, standard deviation, and correlation are computed to analyze the data.


```python
data.describe().show()

print("Min, Max and Std:")
data.select(
    [min(c).alias(f"{c}_min") for c in data.columns if data.schema[c].dataType != "StringType"]
    + [max(c).alias(f"{c}_max") for c in data.columns if data.schema[c].dataType != "StringType"]
    + [stddev(c).alias(f"{c}_stddev") for c in data.columns if data.schema[c].dataType != "StringType"]
).show()


print("Correlation Analysis:")
data.select(corr("age", "charges").alias("age_charges_corr"), corr("bmi", "charges").alias("bmi_charges_corr")).show()
```

## Handling Categorical Variables

This code transforms categorical variables into numerical representations, preparing the data for machine learning algorithms.


```python
categorical_columns = ["sex", "smoker", "region"]
indexers = [StringIndexer(inputCol=col, outputCol=col + "_index") for col in categorical_columns]
encoders = [OneHotEncoder(inputCol=col + "_index", outputCol=col + "_encoded") for col in categorical_columns]
```

## BMI Categorization and Grouping

BMI values are categorized into specific groups, and the data is grouped to count the number of entries in each category.


```python
data = data.withColumn(
    "bmi_category",
    when(col("bmi") < 18.5, lit("underweight"))
    .when((col("bmi") >= 18.5) & (col("bmi") < 25), lit("normal"))
    .when((col("bmi") >= 25) & (col("bmi") < 30), lit("overweight"))
    .otherwise(lit("obese")),
)

data.groupBy("bmi_category").count().show()
```

## Feature Vector Assembly

The specified numerical and encoded categorical columns are combined into a single feature vector column, which is essential for machine learning models.


```python
feature_columns = ["age", "bmi", "children", "sex_encoded", "smoker_encoded", "region_encoded"]
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
```

## Scaling Features and Applying a Pipeline

A pipeline is created to process data by combining categorical encoding, feature vector assembly, and feature scaling into a sequential workflow. This ensures a clean and efficient transformation of raw data into a format suitable for machine learning.


```python
scaler = StandardScaler(inputCol="features", outputCol="scaled_features", withStd=True, withMean=False)

pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler])
data = pipeline.fit(data).transform(data)

data.select("features", "scaled_features").show(5, truncate=False)
```

## Writing Processed Data to a Parquet File and Stopping Spark Session

The processed DataFrame is saved in a Parquet format, and the Spark session is gracefully terminated to release resources.


```python
output_path = "/home/ubuntu/my/processed_insurance_data.parquet"
data.write.parquet(output_path, mode="overwrite")

spark.stop()
```


---

**Previous**: [SparkML Ice Cream](../ice-cream/sparkml-ice-cream.md) | **Next**: [Spark With Job > Batch Job](../spark-with-job/batch-job.md)
