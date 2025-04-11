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
