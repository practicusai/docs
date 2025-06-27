# Trino Data Query API using FastAPI

This document describes a Python-based API service built with `practicuscore` that queries customer data from Trino. It covers the API definition, deployment process, and various methods for testing the deployed API.

## 1. Trino Data Query API (`apis/home.py`)

This Python code defines an API endpoint that retrieves customer information from a Trino database. It uses Pydantic for data validation and `trino` client for database connectivity.

```python
from datetime import date
from pydantic import BaseModel
from fastapi import HTTPException
import practicuscore as prt
import trino
import trino.auth

# Pydantic model for Customer data
class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    signup_date: date

    # Example for API documentation (Swagger/Redoc)
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

# Pydantic model for the API request payload
class CustomerIdRequest(BaseModel):
    customer_id: int

# Pydantic model for the API response
class CustomerResponse(BaseModel):
    customer: Customer

# API endpoint definition using practicuscore decorator
@prt.api("/customer-by-id")
async def get_customer_by_id(payload: CustomerIdRequest, **kwargs) -> CustomerResponse:
    """
    Retrieves customer details from Trino based on customer_id.
    """
    try:
        # Parse and validate the incoming payload
        parsed_payload = CustomerIdRequest.parse_obj(payload)

        # Establish connection to Trino
        # Note: 'verify=False' is used here for demonstration,
        # but in production, proper SSL certificate verification should be configured.
        # BasicAuthentication is used for simplicity, consider more secure methods like Kerberos if available.
        conn = trino.dbapi.connect(
            host="{<TRINO_HOST>}", # e.g., trino.dev.practicus.io
            port=443,
            http_scheme="http}",
            verify=False, # e.g., False (for testing), True (for production with valid certs)
            auth=trino.auth.BasicAuthentication("{<TRINO_USERNAME>}", "{<TRINO_PASSWORD>}"), 
        )
        cursor = conn.cursor()

        # SQL query to fetch customer data
        # Using parameterized query (?) for security against SQL injection
        query = "SELECT customer_id, first_name, last_name, email, phone, signup_date FROM lakehouse.<schema_name>.<customer_table> WHERE customer_id = ?"
        cursor.execute(query, (parsed_payload.customer_id,))
        row = cursor.fetchone()

        # Handle case where customer is not found
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Map query results to the Pydantic Customer model
        columns = [col[0] for col in cursor.description]
        customer = Customer(**dict(zip(columns, row)))

        # Return the CustomerResponse
        return CustomerResponse(customer=customer)

    except HTTPException as http_exc:
        # Re-raise explicit HTTPExceptions
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors and return a generic 500 error
        # In a production environment, log the full exception details here for debugging
        print(f"An unexpected error occurred: {e}") # Log the actual error
        raise HTTPException(status_code=500, detail="Internal server error")

```

**Explanation:**

* Pydantic Models: `Customer`, `CustomerIdRequest`, and `CustomerResponse` define the structure of data for validation and clear API schema generation.
* `@prt.api("/customer-by-id")`: This decorator from `practicuscore` exposes the `get_customer_by_id` function as an API endpoint accessible at `/customer-by-id`.
* Trino Connection: A connection to Trino is established using `trino.dbapi.connect()`, specifying the host, port, scheme, and authentication. Sensitive credentials and hostnames are replaced with placeholders.
* Parameterized Query: The SQL query uses a `?` placeholder for `customer_id` to prevent SQL injection vulnerabilities.
* Error Handling: The API handles cases where a customer is not found (404) and general internal server errors (500).

## 2. API Deployment (`deploy_app.py`)

This script handles the deployment of the application to the Practicus.

```python
import practicuscore as prt

# Deployment configuration variables
app_deployment_key = "{<YOUR_DEPLOYMENT_KEY>}" # e.g., "appdepl-1"
app_prefix = "{<YOUR_APP_PREFIX>}" # e.g., "apps"

# Application metadata
app_name = "{<YOUR_APP_NAME>}" # e.g., "trino-app-1"
visible_name = "Trino API App"
description = "This API retrieves customer details from Trino using the provided customer_id. It returns basic information such as name, email, phone, and signup date."
icon = "fa-rocket" # Font Awesome icon class

# Deploy the application
app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None, # Assuming the API code is in a standard location relative to the deployment script
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("Booting UI :", app_url)
print("Booting API:", api_url)
print("API Docs   :", api_url + "redoc/")
```

**Explanation:**

* `prt.apps.deploy()`: This function deploys the API. It requires a `deployment_setting_key` to specify the deployment environment, a `prefix` for the URL, an `app_name`, and metadata like `visible_name`, `description`, and `icon` for UI visibility.
* The script prints the base URLs for the deployed UI (if any) and the API, including the URL for the auto-generated API documentation (Redoc).

## 3. API Testing - Internal (`test_api_internal.py`)

This code demonstrates how to test the deployed API using `practicuscore`'s internal testing utilities.

```python
import practicuscore as prt

# Flags to control which parts of the test run
test_ui = True # Not applicable for this API-only test, but kept for context
test_api = True

if test_api:
    # Import the response model from your API definition
    # Assuming 'apis/home.py' defines CustomerResponse
    from apis.home import CustomerResponse

    # Define the payload for the API call
    payload = {"customer_id": 103}

    # Call the API internally using prt.apps.test_api
    response: CustomerResponse = prt.apps.test_api("/customer-by-id", payload=payload)

    # Print the full Pydantic response object
    print(response)
```

**Explanation:**

* `prt.apps.test_api()`: This function allows calling deployed API endpoints directly within the `practicuscore` environment, which is useful for rapid testing during development without making actual HTTP requests.
* It takes the API path and the payload, and returns the Pydantic response model, enabling strong type checking and easy access to data.

## 4. API Testing - External (`test_api_external.py`)

This script shows how to call the deployed API from an external client using the `requests` library. It includes token retrieval for authentication.

```python
import practicuscore as prt
import requests
import json # Import json module for pretty printing

# Base URL for the deployed API
api_base_url = "https://{<YOUR_PRACTICUS_DOMAIN>}/apps/{<YOUR_APP_NAME>}/api/v1/" # e.g., [https://dev.practicus.io/apps/trino-app-1/api/v1/](https://practicustest.vodafone.local/apps/trino-app-1/api/v1/)

token = None  # Initialize token. Get a new token, or reuse existing if not expired
# Retrieve a session token from practicuscore for authentication
token = prt.apps.get_session_token(api_url=api_base_url, token=token)

# Construct the full API endpoint URL
api_url = f"{api_base_url}customer-by-id/"

print(f"Auth Token: {token}")
# Prepare HTTP headers including the Authorization token and content type
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
print(f"Request Headers: {headers}")

# Define the payload for the API request
payload_dict = {"customer_id": 108} # Example customer ID

print(f"\nSending JSON payload to: {api_url}")
print(f"Payload: {json.dumps(payload_dict, indent=2)}") # Pretty print payload

try:
    # Send a POST request to the API endpoint
    resp = requests.post(api_url, json=payload_dict, headers=headers)
    resp.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

    # Parse the JSON response
    response_data = resp.json()

    print("\n--- API Raw Response JSON ---")
    print(json.dumps(response_data, indent=2)) # Pretty print raw JSON response

    # Access and print formatted customer details from the raw JSON dictionary
    if "customer" in response_data:
        customer_data = response_data["customer"]
        print("\n---------- Formatted Customer Details ----------")
        print(
            f"{customer_data.get('signup_date')} tarihinde kayıt olan {customer_data.get('first_name')} "
            f"{customer_data.get('last_name')} adlı müşterinin mail adresi {customer_data.get('email')} "
            f"olup telefonu ise {customer_data.get('phone')} şeklindedir."
        )
    else:
        print("Error: 'customer' key not found in response.")

except requests.exceptions.RequestException as e:
    # Handle HTTP request-specific errors
    print(f"\n--- HTTP Request Failed ---")
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print("Raw response body (if any):")
        print(e.response.text)
    else:
        print("No response body received.")

except Exception as e:
    # Handle any other unexpected errors during response processing
    print(f"\n--- Error Processing Response ---")
    print(f"An unexpected error occurred: {e}")
```

**Explanation:**

* `requests` Library: Used to send HTTP POST requests to the deployed API.
* Authentication: `prt.apps.get_session_token()` is used to securely obtain an authentication token, which is then included in the `Authorization` header.
* Error Handling: Includes `try-except` blocks to catch network errors (`requests.exceptions.RequestException`) and other general exceptions, providing informative error messages.
* The `json.dumps(..., indent=2)` is used to pretty-print JSON responses for better readability in the console output.