---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
app_deployment_key = "appdepl"
app_prefix = "apps"
```

If you don't know your prefixes and deployments you can check them out by using the SDK like down below:

```python
assert app_deployment_key, "Please select an app deployment setting."
assert app_prefix, "Please select an app prefix."
```

### Testing APIs in design time

```python
import practicuscore as prt
from apis.say_hello import SayHelloRequest, SayHelloResponse
from pydantic import BaseModel

payload = SayHelloRequest(name="Alice", email="alice@wonderland.com")

print(issubclass(type(payload), BaseModel))

response: SayHelloResponse = prt.apps.test_api("/say-hello", payload)
print("Greeting message:", response.greeting_message, "(for", response.name, ")")
```

## Deploying the App

Once our development and tests are over, we can deploy the app as a new version.

```python
import practicuscore as prt

app_name = "open-api-test"
visible_name = "OpenAPI Protocol Test"
description = "Testing OpenAPI Protocol"
icon = "fas fa-passport"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("Booting UI :", app_url)
print("Booting API:", api_url)
```

### Understanding App Versions

Practicus AI supports multiple app versions and provides different URLs for each environment:

* Default route: `https://practicus.company.com/apps/my-first-app/` routes to the latest or production version.
* Specific versions:
  * Production: `/prod/`
  * Staging: `/staging/`
  * Latest: `/latest/`
  * Exact version: `/v[version]/`
  * For Practicus AI API service mesh dynamically routes to work, place `version indicator right after /api/`
  * For example:
  * https://practicus.company.com/apps/my-first-app/api/prod/say-hello/
  * https://practicus.company.com/apps/my-first-app/api/v4/say-hello/
  * Please note that ../api/say-hello/v4/ or ../api/say-hello/v4/prod/ will **not** work.


```python
import requests

token = None  # Get a new token, or reuse existing if not expired.
token = prt.apps.get_session_token(api_url=api_url, token=token)
say_hello_api_url = f"{api_url}say-hello/"

headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}

json_data = payload.model_dump_json(indent=2)
print(f"Sending below JSON to: {say_hello_api_url}")
print(json_data)

resp = requests.post(say_hello_api_url, json=json_data, headers=headers)

if resp.ok:
    print("Response text:")
    print(resp.text)
    response_obj = SayHelloResponse.model_validate_json(resp.text)
    print("Response object:")
    print(response_obj)
else:
    print("Error:", resp.status_code, resp.text)
```

```python
print("Listing all apps and their versions I have access to:")
region.app_list.to_pandas()
```

```python
# If you don't know the app_id you can use prefix and app_name
region.delete_app(prefix=app_prefix, app_name=app_name)

try:
    # Deleting an app and all it's versions
    region.delete_app(app_id=123)
except:
    pass
```

```python
try:
    # Deleting a particular version of an app
    region.delete_app_version(app_id=123, version=4)

    # If you don't know the app_id you can use prefix and app_name
    region.delete_app_version(prefix="apps", app_name="my-first-app", version=4)
except:
    pass
```


## Supplementary Files

### apis/convert_to_uppercase.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field


class ConvertToUppercaseRequest(BaseModel):
    text: str
    """The text to be converted to uppercase."""

    model_config = {"use_attribute_docstrings": True, "json_schema_extra": {"examples": [{"text": "hello world"}]}}


class ConvertToUppercaseResponse(BaseModel):
    uppercase_text: str
    """The text converted to uppercase."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"uppercase_text": "HELLO WORLD"}]},
    }


@prt.api("/convert-to-uppercase")
async def run(payload: ConvertToUppercaseRequest, **kwargs) -> ConvertToUppercaseResponse:
    """Convert the provided text to uppercase."""
    return ConvertToUppercaseResponse(uppercase_text=payload.text.upper())

```

### apis/count_words.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field


class CountWordsRequest(BaseModel):
    text: str
    """The text in which to count words."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"text": "Hello world, this is a test."}]},
    }


class CountWordsResponse(BaseModel):
    word_count: int
    """The number of words in the provided text."""

    model_config = {"use_attribute_docstrings": True, "json_schema_extra": {"examples": [{"word_count": 6}]}}


@prt.api("/count-words")
async def run(payload: CountWordsRequest, **kwargs) -> CountWordsResponse:
    """Count the number of words in the given text."""
    word_count = len(payload.text.split())
    return CountWordsResponse(word_count=word_count)

```

### apis/generate_receipt.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class OrderItem(BaseModel):
    item_name: str
    """Name of the item."""

    quantity: int
    """Quantity ordered of the item."""

    unit_price: float
    """Unit price of the item."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"item_name": "Widget", "quantity": 2, "unit_price": 19.99}]},
    }


class GenerateReceiptRequest(BaseModel):
    summary: str
    """Order summary from the processed order."""

    total: float
    """Total cost of the order."""

    items: List[OrderItem]
    """List of order items."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Processed order with 2 items. Total amount: $69.97",
                    "total": 69.97,
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ],
                }
            ]
        },
    }


class GenerateReceiptResponse(BaseModel):
    receipt: str
    """The formatted receipt."""

    timestamp: str
    """Timestamp when the receipt was generated."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "receipt": (
                        "----- RECEIPT -----\n"
                        "Processed order with 2 items. Total amount: $69.97\n"
                        "Items:\n"
                        "Widget: 2 x $19.99 = $39.98\n"
                        "Gadget: 1 x $29.99 = $29.99\n"
                        "Total: $69.97\n"
                        "-------------------"
                    ),
                    "timestamp": "2023-01-01T00:00:00Z",
                }
            ]
        },
    }


@prt.api("/generate-receipt")
async def run(payload: GenerateReceiptRequest, **kwargs) -> GenerateReceiptResponse:
    """Generate a formatted receipt from the processed order data."""
    receipt_lines = ["----- RECEIPT -----", payload.summary, "Items:"]
    for item in payload.items:
        line = f"{item.item_name}: {item.quantity} x ${item.unit_price:.2f} = ${item.quantity * item.unit_price:.2f}"
        receipt_lines.append(line)
    receipt_lines.append(f"Total: ${payload.total:.2f}")
    receipt_lines.append("-------------------")
    receipt_text = "\n".join(receipt_lines)
    timestamp = datetime.utcnow().isoformat() + "Z"
    return GenerateReceiptResponse(receipt=receipt_text, timestamp=timestamp)

```

### apis/process_order.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field
from typing import List


class OrderItem(BaseModel):
    item_name: str
    """Name of the item."""

    quantity: int
    """Quantity ordered of the item."""

    unit_price: float
    """Unit price of the item."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"item_name": "Widget", "quantity": 2, "unit_price": 19.99}]},
    }


class ProcessOrderRequest(BaseModel):
    items: List[OrderItem]
    """A list of items in the order."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ]
                }
            ]
        },
    }


class ProcessOrderResponse(BaseModel):
    total: float
    """Total cost of the order."""

    summary: str
    """Summary of the processed order."""

    items: List[OrderItem]
    """The processed list of order items."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "total": 69.97,
                    "summary": "Processed order with 2 items. Total amount: $69.97",
                    "items": [
                        {"item_name": "Widget", "quantity": 2, "unit_price": 19.99},
                        {"item_name": "Gadget", "quantity": 1, "unit_price": 29.99},
                    ],
                }
            ]
        },
    }


@prt.api("/process-order")
async def run(payload: ProcessOrderRequest, **kwargs) -> ProcessOrderResponse:
    """Process an order by calculating the total cost and generating a summary."""
    total = sum(item.quantity * item.unit_price for item in payload.items)
    summary = f"Processed order with {len(payload.items)} items. Total amount: ${total:.2f}"
    return ProcessOrderResponse(total=total, summary=summary, items=payload.items)

```

### apis/say_hello.py
```python
import practicuscore as prt
from enum import Enum

from pydantic import BaseModel, Field


class HelloType(str, Enum):
    NORMAL = "NORMAL"
    CHEERFUL = "CHEERFUL"
    SAD = "SAD"


class SayHelloRequest(BaseModel):
    name: str
    """This is the name of the person"""

    email: str | None = Field(None, description="This is the email")

    hello_type: HelloType = HelloType.NORMAL
    """What kind of hello shall I tell"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"name": "Alice", "email": "alice@wonderland.com"},
                {"name": "Bob", "hello_type": "CHEERFUL", "email": "bob@wonderland.com"},
            ]
        },
    }


class SayHelloResponse(BaseModel):
    greeting_message: str
    """This is the greeting message"""

    name: str
    """Which person we greeted"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"greeting_message": "Hello Alice", "name": "Alice"},
                {"greeting_message": "Hello Bob!!", "name": "Bob"},
            ]
        },
    }


@prt.api("/say-hello")
async def run(payload: SayHelloRequest, **kwargs) -> SayHelloResponse:
    """This method is awesome, it does fantastic things"""

    if payload.hello_type == HelloType.NORMAL:
        return SayHelloResponse(greeting_message=f"Hello {payload.name}", name=payload.name)
    if payload.hello_type == HelloType.CHEERFUL:
        return SayHelloResponse(greeting_message=f"Hello {payload.name}!!", name=payload.name)
    if payload.hello_type == HelloType.SAD:
        return SayHelloResponse(greeting_message=f"Hello {payload.name} :(", name=payload.name)

    raise ValueError(f"Unknown hello type {payload.hello_type}")

```

### apis/send_confirmation.py
```python
import practicuscore as prt
from pydantic import BaseModel, Field


class SendConfirmationRequest(BaseModel):
    receipt: str
    """The receipt text to be used in the confirmation message."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "receipt": (
                        "----- RECEIPT -----\n"
                        "Processed order with 2 items. Total amount: $69.97\n"
                        "Items:\n"
                        "Widget: 2 x $19.99 = $39.98\n"
                        "Gadget: 1 x $29.99 = $29.99\n"
                        "Total: $69.97\n"
                        "-------------------"
                    )
                }
            ]
        },
    }


class SendConfirmationResponse(BaseModel):
    confirmation_message: str
    """The confirmation message including the receipt."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "confirmation_message": (
                        "Order confirmed! Here is your receipt:\n"
                        "----- RECEIPT -----\n"
                        "Processed order with 2 items. Total amount: $69.97\n"
                        "Items:\n"
                        "Widget: 2 x $19.99 = $39.98\n"
                        "Gadget: 1 x $29.99 = $29.99\n"
                        "Total: $69.97\n"
                        "-------------------"
                    )
                }
            ]
        },
    }


@prt.api("/send-confirmation")
async def run(payload: SendConfirmationRequest, **kwargs) -> SendConfirmationResponse:
    """Send an order confirmation message based on the provided receipt."""
    confirmation_message = f"Order confirmed! Here is your receipt:\n{payload.receipt}"
    return SendConfirmationResponse(confirmation_message=confirmation_message)

```


---

**Previous**: [Milvus Chain](../milvus-embedding-and-langchain/milvus-chain.md) | **Next**: [Langflow Apis > Langflow API](../langflow-apis/langflow-api.md)
