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

# Using Practicus AI neo4j Graph DB

This example demonstrates how to:

1. Connect to a Neo4j database using the official Python driver.
2. Create a few example nodes and relationships.
3. Query and print the results.
4. **Clean up** the created data so the notebook is **idempotent** (you can run it multiple times without filling the database with duplicates).

> ⚠️ Replace the connection details (`uri`, `user`, `password`) with the ones that match your own deployment if needed.



## 1. Import the Neo4j Python driver

`neo4j` driver should already be installed on Practicus AI design time and runtime systems. 

If not, you can install running `pip install neo4j`

Then, import the driver and define the connection parameters for your Neo4j instance.


```python
from neo4j import GraphDatabase

# Connection parameters for the Neo4j instance
# Replace these with the values for your own environment if needed.
uri: str = "bolt://practicus-neo4j.prt-ns-neo4j.svc.cluster.local:7687"
user: str = "neo4j"
password: str = "prt-neo4j"

# Create a driver instance. This does not open a session yet.
driver = GraphDatabase.driver(uri, auth=(user, password))

print("Neo4j driver created. Ready to open a session.")

```

## 2. Define a write transaction function

The function below encapsulates a **single write transaction** that will:

1. Create three `Person` nodes: **Alice**, **Bob**, and **Charlie**.
2. Create a `KNOWS` relationship from Alice to Bob.
3. Query and print all people in the database.
4. Query and print Alice's friends.
5. **Clean up** by deleting the sample nodes it just created, so that running this notebook multiple times does not permanently modify your graph.


```python
def create_and_query_nodes(tx) -> None:
    """Create sample nodes and relationships, run a few queries, then clean up.

    This function is meant to be executed inside a Neo4j write transaction.
    """

    # 1) Create sample Person nodes
    tx.run(
        """
        CREATE (:Person {name: 'Alice'}),
               (:Person {name: 'Bob'}),
               (:Person {name: 'Charlie'})
        """
    )

    # 2) Create a KNOWS relationship: Alice -> Bob
    tx.run(
        """
        MATCH (a:Person {name: 'Alice'}),
              (b:Person {name: 'Bob'})
        CREATE (a)-[:KNOWS]->(b)
        """
    )

    # 3) Query for all people
    result = tx.run("MATCH (p:Person) RETURN p.name AS name ORDER BY name")
    print("People in the database:")
    for record in result:
        print(f"- {record['name']}")

    # 4) Query for Alice's friends
    result = tx.run(
        """
        MATCH (a:Person {name: 'Alice'})-[:KNOWS]->(friend)
        RETURN friend.name AS friend_name
        ORDER BY friend_name
        """
    )
    print("\nAlice's friends:")
    for record in result:
        print(f"- {record['friend_name']}")

    # 5) Clean up: delete only the nodes we created in this example
    #    This keeps the notebook safe to run multiple times without
    #    permanently adding duplicate test data.
    tx.run(
        """
        MATCH (p:Person)
        WHERE p.name IN ['Alice', 'Bob', 'Charlie']
        DETACH DELETE p
        """
    )

    print("\nCleanup complete: Alice, Bob, and Charlie have been removed.")

```

## 3. Run the transaction and close the driver

Now we:

1. Open a **session** using the driver.
2. Execute our `create_and_query_nodes` function inside a **write transaction** using `session.execute_write`.
3. Close the driver when we are done.

After running the cell below, you should see the printed people and friendships, followed by a cleanup message.


```python
with driver.session() as session:
    session.execute_write(create_and_query_nodes)

# Always close the driver when you are done with it
driver.close()

print("Done. Driver closed.")

```

## 4. What you should see

Typical output from the transaction cell will look like this:

```text
People in the database:
- Alice
- Bob
- Charlie

Alice's friends:
- Bob

Cleanup complete: Alice, Bob, and Charlie have been removed.
Done. Driver closed.
```

Because we clean up at the end, you can safely re-run the notebook multiple times without accumulating duplicate nodes in your Neo4j database.



---

**Previous**: [Use Polars](use-polars.md) | **Next**: [Personal Startup Scripts](personal-startup-scripts.md)
