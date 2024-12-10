import practicuscore as prt 

# Let's get a Spark session
print("Getting Spark session")
spark = prt.distributed.get_client()

data = [("Alice", 29), ("Bob", 34), ("Cathy", 23)]
columns = ["Name", "Age"]

print("Creating DataFrame")
df = spark.createDataFrame(data, columns)

print("Calculating")
df_filtered = df.filter(df.Age > 30)

print("Writing to csv")
df_filtered.write.csv("/home/ubuntu/my/spark/result.csv", header=True, mode="overwrite")
