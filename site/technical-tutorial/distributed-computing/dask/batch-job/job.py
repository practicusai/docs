import practicuscore as prt 
import dask.dataframe as dd

# Let's get a Dask session
print("Getting Dask session")
dask = prt.distributed.get_client()

print("Reading diamond data")
df = dd.read_csv('/home/ubuntu/samples/diamond.csv')  

print("Calculating")
df["New Price"] = df["Price"] * 0.8

print("Since Dask is a lazy execution engine,")
print(" actual calculations will happen when you call compute() or save.")

print("Saving")
df.to_csv('/home/ubuntu/my/dask/result.csv')

# Note: the save location must be accessible by all workers
# A good place to save for distributed processing is object storage
