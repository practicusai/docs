import practicuscore as prt

print("Requesting a Spark session...")
spark = prt.distributed.get_client()

# Create a sample DataFrame
data = [("Alice", 29), ("Bob", 34), ("Cathy", 23)]
columns = ["Name", "Age"]
print("Creating DataFrame...")
df = spark.createDataFrame(data, columns)

print("Applying filter: Age > 30")
df_filtered = df.filter(df.Age > 30)

print("Filtered results:")
df_filtered.show()

# Note:
# Auto-scaled Spark executors are different from standard Practicus AI workers.
# They use a specialized container image and do not have direct access to
# `~/my` or `~/shared` directories.
# For saving results, consider using a data lake or object storage.
