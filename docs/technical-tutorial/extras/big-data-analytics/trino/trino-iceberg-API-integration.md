---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# Trino, Iceberg, and API Integration

This notebook guides you through setting up a `customer_table` within a Trino Lakehouse environment, injecting sample data, deploying an API endpoint using `practicuscore` to query this table, and finally demonstrating how to interact with the deployed API.


## Trino and Iceberg

### Establishing Trino Connection

Before interacting with Trino, we need to establish a connection. This cell sets up the Trino connection.

```python
import trino

external_access = True

if external_access:
    host = '<TRINO_EXTERNAL_HOST>' # Replace with your actual Trino external host
    port = 443
    verify = True
    # In this scenario, https traffic will be terminated at the load balancer 
    # and Trino will receive http traffic
else:
    host = '<TRINO_INTERNAL_HOST>' # Replace with your actual Trino internal host
    port = 8443 # In this scenario, Trino must receive https traffic

# verify = "ca_cert.pem"
# Disabling SSL verification might not work in some cases
# Either use a global Certificate Authority (CA), or provide the ca_cert.pem
# verify = False

# Create a connection to Trino
conn = trino.dbapi.connect(
    host=host,
    port=port,
    http_scheme='https',
    verify=verify, 
    auth=trino.auth.BasicAuthentication("<USER_NAME>", "<PASSWORD>") # Basic authentication
)
```

### Creating Schema and Table

Now, we'll create the necessary schema (namespace) and the `customer_table` within your specified Lakehouse catalog. The `IF NOT EXISTS` clause prevents errors if the schema or table already exists.

**Note**: The `LAKEHOUSE_CATALOG` and `S3_BUCKET_NAME` values are typically sourced from your Practicus Analytics environment's deployment `YAML` configurations (e.g., `prt-ns-analytics`).

```python
LAKEHOUSE_CATALOG = 'lakehouse' # Your Trino Lakehouse catalog name (e.g., 'lakehouse'). Refer to your YAML configs.
SCHEMA_NAME = 'customers' # The schema (namespace) name you want to use (e.g., 'customers', 'sales', 'test')
TABLE_NAME = 'customer_table' # The name of the table to be created
S3_BUCKET_NAME = 'trino' # The name of your S3-compatible storage bucket (e.g., 'my-data-lake-bucket'). Refer to your YAML configs.
```

```python
cursor = conn.cursor()

if conn and cursor:
    try:
        # Create schema without semicolon
        query_create_schema = f"CREATE SCHEMA IF NOT EXISTS {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}"
        cursor.execute(query_create_schema)
        print(f"Schema '{LAKEHOUSE_CATALOG}.{SCHEMA_NAME}' ensured to exist.")

        # Create table without semicolon
        query_create_table = f"""CREATE TABLE IF NOT EXISTS {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME} (
            customer_id BIGINT,
            first_name VARCHAR,
            last_name VARCHAR,
            email VARCHAR,
            phone VARCHAR,
            signup_date DATE
        )
        WITH (
            format = 'PARQUET',
            location = 's3a://{S3_BUCKET_NAME}/{SCHEMA_NAME}/{TABLE_NAME}'
        )"""
        cursor.execute(query_create_table)
        print(f"Table '{LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME}' created successfully (or already exists).")

        # Show the table DDL
        query_show_table = f"SHOW CREATE TABLE {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME}"
        cursor.execute(query_show_table)
        ddl_result = cursor.fetchone()
        print("\n--- SHOW CREATE TABLE Output ---")
        print(ddl_result[0])

        # Optional: also describe the table
        query_describe_table = f"DESCRIBE {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME}"
        cursor.execute(query_describe_table)
        describe_result = cursor.fetchall()
        print("\n--- DESCRIBE TABLE Output ---")
        for row in describe_result:
            print(row)

    except Exception as e:
        print(f"Error during schema/table creation: {e}")
else:
    print("Trino connection not established. Cannot create schema/table.")

conn.close()
```

```text
Schema 'lakehouse.customers' ensured to exist.
Table 'lakehouse.customers.customer_table' created successfully (or already exists).

--- SHOW CREATE TABLE Output ---
CREATE TABLE lakehouse.customers.customer_table (
   customer_id bigint,
   first_name varchar,
   last_name varchar,
   email varchar,
   phone varchar,
   signup_date date
)
WITH (
   format = 'PARQUET',
   format_version = 2,
   location = 's3a://trino/customers/customer_table',
   max_commit_retry = 4
)

--- DESCRIBE TABLE Output ---
['customer_id', 'bigint', '', '']
['first_name', 'varchar', '', '']
['last_name', 'varchar', '', '']
['email', 'varchar', '', '']
['phone', 'varchar', '', '']
['signup_date', 'date', '', '']
```


### Injecting Sample Data

With the table created, let's inject a comprehensive set of sample customer data. This multi-row `INSERT` statement efficiently populates the table for testing purposes.

```python
if conn and cursor:
    try:
        # SQL DML to insert multiple rows of sample data
        query_insert_data = f"""INSERT INTO {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME} VALUES
        (101, 'John', 'Doe', 'john.doe@example.com', '555-1234', DATE '2025-01-01'),
        (102, 'Jane', 'Smith', 'jane.smith@example.com', '555-5678', DATE '2025-01-02'),
        (103, 'Robert', 'Johnson', 'robert.johnson@example.com', '555-8765', DATE '2025-01-03'),
        (104, 'Emily', 'Williams', 'emily.williams@example.com', '555-4321', DATE '2025-01-04'),
        (105, 'Michael', 'Brown', 'michael.brown@example.com', '555-3456', DATE '2025-01-05'),
        (106, 'Emma', 'Davis', 'emma.davis@example.com', '555-7890', DATE '2025-01-06'),
        (107, 'Daniel', 'Garcia', 'daniel.garcia@example.com', '555-6543', DATE '2025-01-07'),
        (108, 'Olivia', 'Martinez', 'olivia.martinez@example.com', '555-2109', DATE '2025-01-08'),
        (109, 'James', 'Lopez', 'james.lopez@example.com', '555-8901', DATE '2025-01-09'),
        (110, 'Sophia', 'Hernandez', 'sophia.hernan@example.com', '555-0987', DATE '2025-01-10'),
        (111, 'Liam', 'Young', 'liam.young@example.com', '555-7777', DATE '2025-01-11'),
        (112, 'Ava', 'Lee', 'ava.lee@example.com', '555-9999', DATE '2025-01-12'),
        (113, 'Ethan', 'Gonzalez', 'ethan.gonzalez@example.com', '555-1230', DATE '2025-01-13'),
        (114, 'Mia', 'Nelson', 'mia.nelson@example.com', '555-5670', DATE '2025-01-14'),
        (115, 'William', 'Carter', 'william.carter@example.com', '555-4320', DATE '2025-01-15'),
        (116, 'Isabella', 'Mitchell', 'isabella.mitch@example.com', '555-3450', DATE '2025-01-16'),
        (117, 'Alexander', 'Perez', 'alexander.perez@example.com', '555-7895', DATE '2025-01-17'),
        (118, 'Charlotte', 'Roberts', 'charlotte.r@example.com', '555-6545', DATE '2025-01-18'),
        (119, 'Benjamin', 'Turner', 'benjamin.turner@example.com', '555-2105', DATE '2025-01-19'),
        (120, 'Amelia', 'Phillips', 'amelia.p@example.com', '555-8905', DATE '2025-01-20')"""
        cursor.execute(query_insert_data)
        print(f"Sample data inserted successfully into '{LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME}'.")
    except Exception as e:
        print(f"Error inserting sample data: {e}")
else:
    print("Trino connection not established. Cannot insert data.")
```

```text
Sample data inserted successfully into 'lakehouse.customers.customer_table'.
```


### Querying Sample Data

The following code snippet executes a query to retrieve and display a limited set of records from the specified table based on a given condition.

```python
cursor = conn.cursor()
query_select = f"""SELECT * FROM {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME} WHERE signup_date > DATE '2025-01-15' LIMIT 10"""
cursor.execute(query_select)
results = cursor.fetchall()

print(f"\n--- First 10 Rows from {TABLE_NAME} ---")
for row in results:
    print(row)
conn.close()
```

```text
--- First 10 Rows from customer_table ---
[116, 'Isabella', 'Mitchell', 'isabella.mitch@example.com', '555-3450', datetime.date(2025, 1, 16)]
[117, 'Alexander', 'Perez', 'alexander.perez@example.com', '555-7895', datetime.date(2025, 1, 17)]
[118, 'Charlotte', 'Roberts', 'charlotte.r@example.com', '555-6545', datetime.date(2025, 1, 18)]
[119, 'Benjamin', 'Turner', 'benjamin.turner@example.com', '555-2105', datetime.date(2025, 1, 19)]
[120, 'Amelia', 'Phillips', 'amelia.p@example.com', '555-8905', datetime.date(2025, 1, 20)]
```


## API 

### Definition and Deployment

This section defines our API endpoint, which acts as the interface to query our Trino table. We'll then use `practicuscore` to deploy this API.


### API Endpoint Definition and File Creation

Here are the steps to manually add the API code:
- In your current working directory, create a new folder named `apis`.
- Inside the `apis` folder, create a new file called `trino_api.py`.
- Open `trino_api.py` with a text editor of your choice.
- Copy the entire provided API code and paste it into `trino_api.py`.
- The placeholders `LAKEHOUSE_CATALOG`, `SCHEMA_NAME`, and `TABLE_NAME` in the query string must be replaced by the user with the actual catalog, schema, and table names defined earlier in their environment or notebook cells to ensure the query works correctly.
- Save and close the file.

```python
from datetime import date
from pydantic import BaseModel
import practicuscore as prt
import trino
import trino.auth

class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    signup_date: date

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": 101,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-1234",
                    "signup_date": "2025-01-01"
                }
            ]
        }
    }

class CustomerIdRequest(BaseModel):
    customer_id: int

class CustomerResponse(BaseModel):
    customer: Customer

@prt.api("/customer-by-id")
async def get_customer_by_id(payload: CustomerIdRequest, **kwargs) -> CustomerResponse:
    try:
        parsed_payload = CustomerIdRequest.parse_obj(payload)

        conn = trino.dbapi.connect(
            host="<TRINO_EXTERNAL_HOST>",  # Replace with your actual Trino external host
            port=443,
            http_scheme="https",
            verify=False,
            auth=trino.auth.BasicAuthentication("<USER_NAME>", "<PASSWORD>")  # Basic authentication,
        )
        cursor = conn.cursor()

        query = "SELECT customer_id, first_name, last_name, email, phone, signup_date FROM {LAKEHOUSE_CATALOG}.{SCHEMA_NAME}.{TABLE_NAME} WHERE customer_id = ?"
        cursor.execute(query, (parsed_payload.customer_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")

        columns = [col[0] for col in cursor.description]
        customer = Customer(**dict(zip(columns, row)))

        return CustomerResponse(customer=customer)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # For production, you'd typically log the full error here
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Internal Test of API

This Python code snippet demonstrates a basic interaction with a hypothetical practicuscore API to retrieve customer information.

```python
from apis.trino_api import CustomerResponse
import practicuscore as prt

payload = {"customer_id": 103}
response: CustomerResponse = prt.apps.test_api("/customer-by-id", payload=payload)

print(response)
```

```text
customer=Customer(customer_id=103, first_name='Robert', last_name='Johnson', email='robert.johnson@example.com', phone='555-8765', signup_date=datetime.date(2025, 1, 3))
```


### API Deployment 

This section describes the Python code responsible for defining and deploying an API using the `practicuscore` framework.

```python
app_deployment_key = "appdepl-1"
app_prefix = "apps"

app_name = "trino-app"
visible_name = "Trino API App"
description = "This API retrieves customer details from Trino using the provided customer_id. It returns basic information such as name, email, phone, and signup date."
icon = "fa-rocket"

import practicuscore as prt 

# Deploy the API
app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,  # Use None to deploy from the current directory
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("\n--- API Deployment Details ---")
print("Booting UI  :", app_url)
print("Booting API :", api_url)
print("API Docs    :", api_url + "redoc/")
```

### Querying Data via the Deployed API

Finally, we'll make an actual `HTTP` request to the deployed API to retrieve customer data. This demonstrates the end-to-end functionality.

```python
import practicuscore as prt 

token = None  # Get a new token, or reuse existing, if not expired
token = prt.apps.get_session_token(api_url=api_url, token=token)
print(api_url)
customer_by_id_api_url = f"{api_url}customer-by-id/"
print(customer_by_id_api_url)
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
```

```python
import requests

payload_dict = {"customer_id": 108}

try:
    resp = requests.post(customer_by_id_api_url, json=payload_dict, headers=headers)
    resp.raise_for_status() # Raise for HTTP errors

    # Work directly with the raw JSON dictionary
    response_data = resp.json()

    print("\n--- API Raw Response JSON ---")
    print(response_data)

except requests.exceptions.RequestException as e:
    print(f"\n--- HTTP Request Failed ---")
    print(f"Error: {e}")
    print("Raw response body (if any):")
    print(resp.text)

except Exception as e:
    print(f"\n--- Error Processing Response ---")
    print(f"An unexpected error occurred: {e}")
```

```text
--- API Raw Response JSON ---
{'customer': {'customer_id': 108, 'first_name': 'Olivia', 'last_name': 'Martinez', 'email': 'olivia.martinez@example.com', 'phone': '555-2109', 'signup_date': '2025-01-08'}}
```


This interactive notebook provides a complete walk-through from setting up your Trino environment to deploying and consuming a data API. 


---

**Previous**: [Spark Object Storage](../../data-processing/process-data/spark-object-storage.md)
