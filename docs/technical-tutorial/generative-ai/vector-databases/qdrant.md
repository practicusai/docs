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

# Qdrant vector database sample

This example demonstrates the basic operations using `qdrant-client`, the Python SDK for the Qdrant vector database.

## Before you begin

Please make sure that you have access to a running Qdrant instance and have installed the `qdrant-client` library (`pip install qdrant-client`).

```python
# Qdrant connection details (replace with your actual endpoint and key if needed)
# Ensure the Qdrant instance is running and accessible from this notebook environment.
QDRANT_URL = "http://practicus-qdrant.prt-ns-qdrant.svc.cluster.local:6333"  # Example URL from request
QDRANT_API_KEY = "my-api-key"  # Example API Key from request (use None if no key is required)
```

```python
assert QDRANT_URL, "Please enter your Qdrant connection URL in the cell above."
```

## Steps 

1. Connect to Qdrant
2. Create a collection
3. Insert data (Points)
4. Search with filtering
5. Delete points by ID
6. Drop the collection

```python
import numpy as np
import time
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range, PointIdsList

fmt = "\n=== {:30} ===\n"
search_latency_fmt = "search latency = {:.4f}s"

# Parameters from the original notebook
COLLECTION_NAME = "demo_qdrant_collection"  # Renamed for clarity
NUM_ENTITIES, DIM = 3000, 8
```

## Connect to Qdrant

Initialize the Qdrant client using the specified URL and API Key.

```python
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=60,  # Optional: Increase timeout for slow connections or large operations
)

# Optional: Check connection by listing collections or getting cluster info
try:
    # Attempt to get cluster info as a basic health check
    cluster_info = client.info()
    print("Successfully connected to Qdrant.")
    print(f"Qdrant cluster info: {cluster_info}")
except Exception as e:
    print(f"Failed to connect to Qdrant or get cluster info: {e}")
    # Depending on the error, you might want to stop execution here
    # raise e
```

## Create a collection

We'll create a collection named `demo_qdrant_collection`.

Qdrant allows defining the vector parameters (size and distance metric) during collection creation.

We will use:
- **size**: The dimension of the vectors (DIM=8).
- **distance**: The distance metric for similarity search (e.g., Cosine, Dot, Euclid). We'll use Cosine here.

```python
# Ensure the collection doesn't already exist for a clean run
try:
    print(f"Checking if collection '{COLLECTION_NAME}' exists...")
    collection_exists = client.collection_exists(collection_name=COLLECTION_NAME)

    if collection_exists:
        print(f"Collection '{COLLECTION_NAME}' already exists. Deleting it first.")
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' deleted. Waiting a moment...")
        time.sleep(2)  # Give Qdrant a moment to process the deletion
    else:
        print(f"Collection '{COLLECTION_NAME}' does not exist. Proceeding to create.")

    # Create the collection
    print(f"Creating collection '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
        # Optional: Add optimizers_config, hnsw_config, quantization_config etc. here if needed
        # Example: optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
        # Example: hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100)
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")

except Exception as e:
    print(f"An error occurred during collection setup: {e}")
    # raise e

# Verify creation by getting collection info
try:
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    print(fmt.format("Collection Info"))
    print(collection_info)
except Exception as e:
    print(f"Error getting collection info for '{COLLECTION_NAME}': {e}")
```

## Insert data (Points)

We are going to insert `NUM_ENTITIES` (3000) points into the collection.

Each point requires:
- `id`: A unique identifier (integer or UUID string). We'll use integers here for simplicity.
- `vector`: The vector embedding.
- `payload` (optional): Additional data associated with the vector (like the 'random' field from the original notebook).

```python
print(fmt.format("Prepare Data"))
rng = np.random.default_rng(seed=19530)
random_payload_data = rng.random(NUM_ENTITIES).tolist()  # field 'random'
embedding_vectors = rng.random((NUM_ENTITIES, DIM)).astype("float32")  # field 'embeddings'

# Generate simple integer IDs
point_ids = list(range(NUM_ENTITIES))
# Alternatively, use UUIDs (recommended for production):
# point_ids = [str(uuid.uuid4()) for _ in range(NUM_ENTITIES)]

# Create PointStruct objects
points_to_insert = [
    PointStruct(
        id=point_ids[i],
        vector=embedding_vectors[i].tolist(),  # Pass vector as a list
        payload={"random": random_payload_data[i]},  # Payload is a dictionary
    )
    for i in range(NUM_ENTITIES)
]
print(f"Prepared {len(points_to_insert)} points for insertion.")

print(fmt.format("Insert Data"))
# Upsert points into the collection
# `upsert` inserts new points or updates existing ones with the same ID.
# Using `wait=True` ensures the operation is completed before proceeding.
try:
    # Insert in batches if NUM_ENTITIES is very large
    # batch_size = 500
    # for i in range(0, NUM_ENTITIES, batch_size):
    #    batch_points = points_to_insert[i:i+batch_size]
    #    op_info = client.upsert(collection_name=COLLECTION_NAME, points=batch_points, wait=True)
    #    print(f"Upserted batch {i//batch_size + 1}, status: {op_info.status}")

    # Insert all at once for smaller datasets
    op_info = client.upsert(collection_name=COLLECTION_NAME, points=points_to_insert, wait=True)
    print(f"Upsert operation completed with status: {op_info.status}")

except Exception as e:
    print(f"Error during upsert operation: {e}")
    # raise e

# Check the number of points in the collection
try:
    count_result = client.count(collection_name=COLLECTION_NAME, exact=True)
    print(f"Number of points in collection '{COLLECTION_NAME}': {count_result.count}")
except Exception as e:
    print(f"Error counting points: {e}")
```

## Search with filtering

Qdrant allows filtering search results based on payload fields.

We'll retrieve points where the `random` field is greater than 0.9. For retrieving potentially many results based only on filters, `scroll` is often more suitable than `search`.

```python
print(fmt.format("Search with Filtering (Scroll)"))

# Define the filter: payload field 'random' > 0.9
scroll_filter = Filter(
    must=[
        FieldCondition(
            key="random",  # Payload field key
            range=Range(gt=0.9),  # Condition: greater than 0.9
        )
    ]
)

start_time = time.time()
try:
    # Use scroll to retrieve points matching the filter
    # 'scroll' is suitable for iterating through large result sets.
    scroll_result, next_page_offset = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=scroll_filter,
        limit=10,  # Retrieve first 10 matching points
        with_payload=True,
        with_vectors=False,  # We don't need the vectors for this query
    )
    end_time = time.time()

    print(f"Found {len(scroll_result)} points with 'random' > 0.9 (limit 10):")
    for record in scroll_result:
        print(f"  Point ID: {record.id}, Payload: {record.payload}")
    # You can use next_page_offset to paginate through more results if needed
    # print(f"Next page offset: {next_page_offset}")
    print(search_latency_fmt.format(end_time - start_time))

except Exception as e:
    end_time = time.time()
    print(f"Error during filtered scroll: {e}")
    print(f"Time elapsed before error: {end_time - start_time:.4f}s")
```

## Delete points by ID

You can delete points from the collection using their IDs.

```python
print(fmt.format("Delete Points"))

# IDs to delete (e.g., the first two points we inserted)
# Ensure these IDs exist and match the type used (int or UUID)
ids_to_delete = point_ids[0:2]  # e.g., [0, 1]

# Check points before deletion (optional)
try:
    points_before = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=ids_to_delete,
        with_payload=False,  # Don't need payload for existence check
        with_vectors=False,
    )
    print(f"Points found before deletion for IDs {ids_to_delete}: {len(points_before)}")
    # print(points_before)
except Exception as e:
    print(f"Error retrieving points before deletion: {e}")

# Delete the points
try:
    delete_result = client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=PointIdsList(points=ids_to_delete),
        wait=True,  # Wait for operation to complete
    )
    print(f"Deletion operation completed with status: {delete_result.status}")
except Exception as e:
    print(f"Error during point deletion: {e}")

# Verify deletion (optional)
try:
    points_after = client.retrieve(collection_name=COLLECTION_NAME, ids=ids_to_delete)
    print(f"Points found after deletion for IDs {ids_to_delete}: {len(points_after)}")  # Should be 0

    count_after_delete = client.count(collection_name=COLLECTION_NAME, exact=True)
    print(
        f"Total points remaining in collection: {count_after_delete.count}"
    )  # Should be NUM_ENTITIES - len(ids_to_delete)

except Exception as e:
    print(f"Error retrieving points after deletion: {e}")
```

## Drop the collection

Finally, clean up by dropping the collection.

```python
print(fmt.format("Drop Collection"))
try:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' dropped successfully.")
except Exception as e:
    print(f"Error dropping collection '{COLLECTION_NAME}': {e}")

# Verify deletion
try:
    exists_after_drop = client.collection_exists(collection_name=COLLECTION_NAME)
    print(f"Does collection '{COLLECTION_NAME}' exist after drop? {exists_after_drop}")  # Should be False
except Exception as e:
    print(f"Error checking collection existence after drop: {e}")
```

## Note on Qdrant Admin UI

If your Qdrant instance has the Web UI enabled (which is common), you might be able to access it through a browser. This UI allows you to inspect collections, points, search, and manage the cluster visually.

**Ask your administrator** for the URL and any necessary credentials if you wish to use the Qdrant Admin UI.


---

**Previous**: [Embeddings](../langchain/embeddings.md) | **Next**: [Milvus](milvus.md)
