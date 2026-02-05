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

# Service Orchestration with Message Queues

## Overview

This example demonstrates how to use our **RabbitMQ Helper SDK** (`prt.mq`) to:

- **Declare and configure** RabbitMQ exchanges and queues (if you have permissions)
- **Publish messages** (asynchronously or directly)
- **Consume messages** using background tasks (consumers)
- **Register consumers automatically** (production approach)
- **Export topology** for environments where you do **not** have MQ configuration privileges
- **Leverage advanced features** such as prefetch concurrency, dead-letter exchanges, headers-based routing, and more.

In addition, this notebook shows how to deploy a Practicus AI app that exposes APIs for publishing messages and runs background consumers. Use this guide as both an educational reference and a hands-on example of deploying a complete MQ-based application.

## 1. Introduction to RabbitMQ Basics

In a **GenAI** or multi-agent environment, components often communicate asynchronously:

- Multiple models or agents sharing inference results
- Coordinating tasks across microservices
- Aggregating data streams in near real-time

A robust **message queue** architecture ensures messages do not get lost and that producers/consumers can operate at different speeds without bottlenecking the entire system.

### Key Terms
1. **Exchanges**: Routing agents; messages from producers go here. The exchange then routes to one or more queues based on type/routing key/binding.
2. **Queues**: Store messages until consumed. Durable queues (the default in our SDK) survive RabbitMQ restarts.
3. **Bindings**: Define how an exchange routes messages to a queue (e.g., matching a routing key or header properties).

Our SDK wraps these concepts in a simpler interface, so you can focus on your application rather than boilerplate code.

![RabbitMQ Hello World](img/rabbitmq.png)

For more details on RabbitMQ concepts, visit [RabbitMQ AMQP Concepts](https://www.rabbitmq.com/tutorials/amqp-concepts).

## 2. Basic Configuration & Parameters

The `MQConfig` object holds all the connection and topology parameters:

- `conn_str`: AMQP connection string (e.g., `amqp://user:pass@host/vhost`).
- `exchange`: Name of the exchange (optional).
- `queue`: Name of the queue (required for consumers, optional for publishers if you have an exchange).
- `exchange_type`: ("direct", "topic", "fanout", or "headers"). Defaults to `"direct"`.
- `routing_key`: Routing key to use when publishing.
- `verify_delivery`: If `True`, the SDK sets the **mandatory** flag so unroutable messages are returned by the broker (note that the current code does not attach a return callback).
- `max_retries`: Number of times a message is retried. Defaults to 5.
- `dead_letter_exchange` & `dead_letter_routing_key`: If configured, messages that exceed `max_retries` are sent to a dead-letter exchange.
- `prefetch_count`: Limits the number of messages delivered to a consumer before acknowledgment.
- `headers`: For **headers**-type exchanges (used both in publishing and binding for consuming).
- `queue_ttl`: Time-to-live for messages in a queue, in **milliseconds**.

```python
# Parameters - Adjust As Needed
mq_user = None  # E.g. "guest"
mq_pwd = None  # E.g. "guest"
mq_host = None  # E.g. "prt-mq-default"
mq_vhost = ""  # Recommended for fine-grained security ("/" is default if empty)

# If True, run consumer (background task) code in this notebook
test_consumer = True

# Deployment parameters for our Practicus AI app (for publishing APIs and background consumers)
app_deployment_key = None
app_prefix = "apps"
test_api = True
```

```python
assert mq_user, "Please type your RabbitMQ user"
assert mq_pwd, "Please type your RabbitMQ password"
assert mq_host, "Please type your RabbitMQ host"
assert app_deployment_key, "Please enter your app deployment key"
```

```python
# RabbitMQ connection string
mq_conn_str = f"amqp://{mq_user}:{mq_pwd}@{mq_host}/{mq_vhost}"
```

## 3. Applying or Exporting Your Topology

If you have **administrator privileges** on your RabbitMQ cluster, you can explicitly create (declare) exchanges, queues, and bindings via `prt.mq.apply_topology(...)`. Otherwise, you can generate YAML manifests with `prt.mq.export_topology(...)` and supply them to an admin.

### Example: Declaring Our First Exchange & Queue


```python
import practicuscore as prt

# Our first MQConfig. We'll define an exchange and a queue.
mq_config_basic = prt.MQConfig(
    conn_str=mq_conn_str,
    exchange="my-first-exchange",
    routing_key="my-routing-key",  # Recommended
    queue="my-first-queue",
    exchange_type="direct",
)

await prt.mq.apply_topology(mq_config_basic)
print("Topology applied successfully.")

# If you don't have privileges, you could instead export the topology:
# prt.mq.export_topology(mq_config_basic)
```

## 4. Publishing Messages

### Basic Asynchronous Publishing via an Exchange

When an `exchange` is provided in `MQConfig`, your message is routed by that exchange (and the routing key) to the bound queue(s).

The following example demonstrates sending a Pydantic model (`MyMsg`), which the SDK automatically serializes to JSON.

```python
from pydantic import BaseModel


class MyMsg(BaseModel):
    text: str


async def async_publish_example():
    # Connect asynchronously
    conn = await prt.mq.connect(mq_config_basic)
    async with conn:
        msg = MyMsg(text="Hello from async publisher using exchange!")
        await prt.mq.publish(conn, msg)
        print("Message published asynchronously using exchange.")


# Run the async publisher example
await async_publish_example()
```

### Publishing Directly to a Queue

If you omit `exchange` in `MQConfig`, the SDK publishes to RabbitMQ's default exchange, using the `queue` as the routing key (or `routing_key` if provided).

This approach is simpler but less flexible, as it does not allow for custom routing. **Practicus AI recommends using exchanges for all message publishing.**

```python
# Direct-to-Queue Publishing Example

mq_config_direct = prt.MQConfig(
    conn_str=mq_conn_str,
    queue="my-direct-queue",
)

# Declare the queue (if privileges allow)
await prt.mq.apply_topology(mq_config_direct)


async def async_publish_direct_queue():
    conn = await prt.mq.connect(mq_config_direct)
    async with conn:
        msg = MyMsg(text="Hello directly to queue asynchronously!")
        await prt.mq.publish(conn, msg)
        print("Message published directly to queue asynchronously.")


await async_publish_direct_queue()
```

## 5. Consuming Messages

Our SDK uses the `@prt.mq.consumer` decorator to mark a function as a consumer. The consumer function can have one of two signatures:

1. **Single-parameter function**: The SDK automatically decodes the message (or deserializes it into a Pydantic model if annotated).
2. **Two-parameter function (optional)**: The second optional parameter receives the raw `aio_pika.IncomingMessage` (which gives access to headers and properties).

## Concurrency and Execution Modes (Important)

Our SDK supports **concurrent message processing** and two **execution modes** for consumer handlers.

### 1) Concurrency (How many messages run in parallel?)

Concurrency is controlled primarily by:

- **`MQConfig.prefetch_count`**: maximum number of in-flight (un-acked) messages delivered to a consumer.
  - If `prefetch_count=1`, your consumer processes messages one-at-a-time.
  - If `prefetch_count=8`, your consumer can process up to 8 messages concurrently.
- **Number of registered consumers**: each decorated function registered becomes its own consumer task.
  - If you register 2 consumers with `prefetch_count=8`, you can process ~16 messages concurrently (subject to broker delivery, CPU, I/O, etc.).

**Rule of thumb for novices:** start with `prefetch_count=1` or `prefetch_count=4`, then increase gradually.

### 2) Execution Mode: `execution="thread"` vs `execution="event_loop"`

Consumer functions must be `async def`, but handlers can accidentally include blocking operations (e.g., `requests`, CPU-heavy Pandas).

#### ✅ `execution="thread"` (default, recommended)
- The handler runs in a **worker thread** with its own asyncio event loop.
- Protects the app’s main event loop from blocking code.
- Best for novice teams and mixed sync/async libraries.

**Potential issues / gotchas**
- Global state is still accessible, but must be **thread-safe** if mutated.
- Do **not** reuse async clients created on the main event loop (e.g. a global `ClientSession` created elsewhere). Create async clients inside the handler if needed.

#### ⚡ `execution="event_loop"` (advanced, highest throughput)
- The handler is awaited directly on the app’s main event loop.
- Fastest option, but **any blocking call stalls the whole app**:
  - `requests`, `time.sleep`, heavy CPU loops, large dataframe ops, etc.

**Use event_loop mode only if**
- all I/O uses async libraries (e.g., `httpx.AsyncClient`, async DB drivers),
- CPU-heavy work is explicitly offloaded (`asyncio.to_thread` / process pool),
- you’ve tested under load.

```python
# Example of a Basic Consumer (Single Parameter)

subscriber_config = prt.MQConfig(
    conn_str=mq_conn_str,
    exchange="my-first-exchange",
    routing_key="my-routing-key",
    queue="my-first-queue",
    exchange_type="direct",
    prefetch_count=10,
    max_retries=5,
)


@prt.mq.consumer(subscriber_config)
async def process_message(msg: MyMsg):
    """
    A consumer that expects a Pydantic model.
    """
    print("Received message:", msg.text)
```

### Testing a Consumer in Jupyter

You can test a single consumer using `prt.mq.test_consumer(...)`. **Note:** This will block further cell execution until you interrupt or restart the kernel. In production, consumers will be run in Practicus AI apps as background tasks.

```python
if test_consumer:
    print(
        "Starting consumer. This cell will block until notebook kernel is interrupted or restarted."
    )
    await prt.mq.test_consumer(process_message)
```

```python
import practicuscore as prt

# Example of a Consumer with Two Parameters
subscriber_config_two_params = prt.MQConfig(
    conn_str=mq_conn_str, queue="my-direct-queue"
)


@prt.mq.consumer(subscriber_config_two_params)
async def process_message_twoparams(body, incoming_msg):
    """
    A consumer that receives the decoded message and the raw IncomingMessage
    with properties such as message id.
    """
    print("Received body:", body)
    print("IncomingMessage Properties:")
    for key, value in incoming_msg.properties:
        print(f"- {key}: {value}")
```

```python
if test_consumer:
    print(
        "Starting consumer. This cell will block until notebook kernel is interrupted or restarted."
    )
    await prt.mq.test_consumer(process_message_twoparams)
```

<!-- #region -->
## 6. Production-Ready Consumer (Subscriber) Registration

In a production scenario, you can create one or more Python files that define consumer functions (using the `@prt.mq.consumer` decorator). When the Practicus AI app starts, all consumers will be automatically loaded and run as background asynchronous jobs.

### Example Consumer File:

```python
# mqs/consume.py
import practicuscore as prt
from pydantic import BaseModel

class MyMsg(BaseModel):
    text: str

mq_conn_str = "..."

# Consumer configuration
mq_config = prt.MQConfig(
    conn_str=mq_conn_str,
    queue="my-first-queue",
)

@prt.mq.consumer(mq_config)  # defaults to execution="thread"
async def consume_message(message: MyMsg):
    print(f"Received: {message.text}")

# Advanced: execution="event_loop"
@prt.mq.consumer(mq_config, execution="event_loop")
async def consume_message_fast(message: MyMsg):
    # Only safe if ALL calls are **strictly non-blocking**.
    print(f"[fast] {message.text}")
```

Note: Since we have two consumers connecting to the same queue, incoming messages will be distributed "round-robin". E.g. first message will be handled by consume_message(), second one by consume_message_raw(), third one by consume_message() again ...
<!-- #endregion -->

```python
import practicuscore as prt

# View application deployment settings and application prefixes
region = prt.get_default_region()

my_app_settings = prt.apps.get_deployment_setting_list()

print("Application deployment settings available:")
display(my_app_settings.to_pandas())

my_app_prefixes = prt.apps.get_prefix_list()

print("Application prefixes (groups) available:")
display(my_app_prefixes.to_pandas())
```

```python
assert app_deployment_key, "Please select an app deployment setting."
assert app_prefix, "Please select an app prefix."
```

```python
async def test_publisher():
    from apis.publish import MyMsg

    payload = MyMsg(text="Testing API")

    # Test the publishing API asynchronously
    # You can use prt.apps.test_api()
    response = prt.apps.test_api("/publish", payload)
    print("Response:", response)


if test_api:
    await test_publisher()
```

## 7. Deploying the Practicus AI App

After testing your publishers and consumers locally, you can deploy the Practicus AI app. This deployment creates:

- An API endpoint to accept publish requests
- Background tasks that run your consumer functions

The following code deploys the app and returns both the UI and API URLs.

```python
# Analyze your code before deploying and verify API endpoints and MQ Consumers.
prt.apps.analyze()
```

```python
app_name = "my-mq-app"
visible_name = "My RabbitMQ App"
description = "Application that hosts APIs to publish to RabbitMQ and background consumers to process messages."
icon = "fa-stream"

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("API Endpoint URL:", api_url)
```

```python
def send_request():
    from apis.publish import MyMsg
    import requests

    token = prt.apps.get_session_token(api_url=api_url)
    publish_api_url = f"{api_url}publish/"

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = MyMsg(text="Testing API")

    json_data = payload.model_dump_json(indent=2)
    print(f"Sending the following JSON to: {publish_api_url}")
    print(json_data)

    resp = requests.post(publish_api_url, json=json_data, headers=headers)

    if resp.ok:
        print("Response:")
        print(resp.text)
    else:
        print("Error:", resp.status_code, resp.text)


send_request()
```

```python
async def send_request_async():
    from apis.publish import MyMsg
    import httpx

    token = prt.apps.get_session_token(api_url=api_url)
    publish_api_url = f"{api_url}publish/"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = MyMsg(text="Testing API with an async call")
    data_dict = payload.model_dump()
    print(f"Sending (async) the following JSON to: {publish_api_url}")
    print(data_dict)

    async with httpx.AsyncClient() as client:
        response = await client.post(publish_api_url, json=data_dict, headers=headers)

    if response.status_code < 300:
        print("Response:")
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)


await send_request_async()
```

### Verifying Consumption

- After an API call, the message payload is forwarded to the designated RabbitMQ queue via the exchange.
- Consumers receive the messages in real time, automatically decoding and processing the content while logging the data and associated metadata.
- You can verify successful message consumption by monitoring your application's logs in Grafana or by checking logs directly from your Kubernetes pods.
- If multiple consumers are registered for the same queue (as in the `consume.py` example), messages are distributed round-robin. E.g., the first message is processed by `consume_message()`, the second by `consume_message_raw()`, then the third by `consume_message()`, and so on. If you need both consumer functions to receive the same messages, you can configure two separate queues.
- This end-to-end flow confirms that your API is effectively integrated with the background consumer processes.

### Cleaning-up

Delete the deployed app

```python
prt.apps.delete(prefix=app_prefix, app_name=app_name)
```

## 8. Exporting RabbitMQ Topology for Production
In production environments where you lack permissions to create RabbitMQ resources, use `prt.mq.export_topology(config)` to generate Kubernetes YAML files. You can then apply these via `kubectl apply -f` or use the provided shell scripts.

**Naming Tip:** Ensure that RabbitMQ resource names are RFC 1123 compliant (e.g., `my-exchange` or `my.exchange` instead of `my_exchange`) to avoid issues with Kubernetes resource naming.

```python
# Generating new RabbitMQ topology files for production

mq_user = "new-user"
mq_pwd = "new-user-password"
mq_host = "prt-mq-default"
mq_vhost = "some-vhost"

mq_conn_str = f"amqp://{mq_user}:{mq_pwd}@{mq_host}/{mq_vhost}"

new_config = prt.MQConfig(
    conn_str=mq_conn_str,
    exchange="new-exchange",
    routing_key="new-routing-key",
    queue="new-queue",
    exchange_type="direct",
)

prt.mq.export_topology(new_config)

# For more export options (e.g., hiding passwords), see the help for export_topology().
```

## 9. Advanced Features

### Headers Exchange
If you set `exchange_type="headers"` in `MQConfig`, you can route messages based on custom headers:

- For publishing, set `config.headers` to attach custom headers with your message.
- For consuming, the same `config.headers` is used as binding arguments (with an optional `x-match` property).

### Dead-Letter Exchanges (DLX)
Set `dead_letter_exchange` and optionally `dead_letter_routing_key` in `MQConfig` to route messages that exceed `max_retries` to a dead-letter exchange.

### Prefetch Concurrency
`prefetch_count` limits the number of messages delivered to a consumer before waiting for acknowledgments, helping you control load.

### Verify Delivery
With `verify_delivery=True`, the SDK sets the `mandatory flag` so that if a message is unroutable, the broker returns it. Note that our example implementation does not attach a return callback, so only general connection failures trigger retries.

### Customizing MQ topology templates

If you would like to customize the way Practicus AI auto-generates MQ topology files, please update the corresponding ~/practicus/templates/mq_*.yaml Jinja template file.

## 10. Summary & Next Steps

In this example we have:

1. Introduced RabbitMQ fundamentals (exchanges, queues, bindings).
2. Demonstrated how to create or export topology using `apply_topology` and `export_topology`.
3. Provided examples for asynchronous publishing (both via an exchange and direct to a queue).
4. Shown how to define and test consumers using the SDK (including single and dual-parameter approaches).
5. Explained advanced features such as headers exchanges, dead-lettering, prefetch concurrency, and verify delivery.
6. Illustrated a production-ready pattern for registering consumers from a folder.
7. Demonstrated how to deploy a Practicus AI app that exposes publishing APIs and runs background consumers.

### Next Steps:
- Integrate these examples into your GenAI or microservices pipelines.
- For advanced tracing or logging, extend the SDK or integrate with external systems.
- Customize deployment parameters as needed and consider using secure credential management (e.g., `prt.vault`).


## Supplementary Files

### apis/publish.py
```python
import practicuscore as prt
from pydantic import BaseModel
import asyncio

mq_conn = None
mq_conn_lock = asyncio.Lock()

mq_user = "guest"
mq_pwd = "guest"
mq_host = "prt-mq-default"
mq_vhost = ""  # Recommended for fine-grained security
mq_conn_str = f"amqp://{mq_user}:{mq_pwd}@{mq_host}/{mq_vhost}"

# Assuming queue(s) and binding(s) are already configured.
mq_config = prt.MQConfig(
    conn_str=mq_conn_str,
    exchange="my-first-exchange",
    routing_key="my-routing-key",
)


class MyMsg(BaseModel):
    text: str


async def connect_mq():
    global mq_conn

    if mq_conn is not None:
        return

    # (Recommended) using mq_conn_lock prevents potential thundering-herd reconnects
    async with mq_conn_lock:
        if mq_conn is not None:
            return
        mq_conn = await prt.mq.connect(mq_config)


@prt.apps.api("/publish")
async def publish(payload: MyMsg, **kwargs):
    await connect_mq()

    assert mq_conn, "MQ connection is not initialized"
    await prt.mq.publish(conn=mq_conn, msg=payload)

    return {"ok": True}

```

### mqs/consume.py
```python
import practicuscore as prt
from pydantic import BaseModel


class MyMsg(BaseModel):
    text: str


# In production, please use prt.vault to avoid hard coding the secret in your code
mq_user = "guest"
mq_pwd = "guest"
mq_host = "prt-mq-default"
mq_vhost = ""  # Recommended for fine-grained security
mq_conn_str = f"amqp://{mq_user}:{mq_pwd}@{mq_host}/{mq_vhost}"

# Subscriber configuration
mq_config = prt.MQConfig(
    conn_str=mq_conn_str,
    queue="my-first-queue",
    # prefetch_count=8,   # Higher throughput example: process up to 8 messages concurrently per registered consumer. (Defaults to 1)
)

# If you haven't configured the MQ topology in advance
# prt.mq.apply_topology(mq_conf)


@prt.mq.consumer(mq_config)
async def consume_message(message: MyMsg):
    """
    Consumes an incoming RabbitMQ message, deserializing it into a Pydantic model first.

    **Parameters:**
    - message (MyMsg):
      A Pydantic model instance representing the incoming message.

    **Returns:**
    - None
    """
    print(f"Received message: {message.text}")


@prt.mq.consumer(mq_config)
async def consume_message_raw(message):
    """
    Processes an incoming RabbitMQ message, *without* deserializing into a Pydantic model first.

    **Parameters:**
    - message:
      Binary data representing the incoming message, which will be a json in our test.

    **Returns:**
    - None
    """
    print(f"Received raw message: {message}")


# Advanced: high-throughput mode uses -> execution="event_loop"
@prt.mq.consumer(mq_config, execution="event_loop")
async def consume_message_fast(message: MyMsg):
    """
    Advanced: runs directly on the main event loop instead of a thread.
    Only use if ALL code here is **strictly non-blocking** (async libraries, no CPU-heavy work).
    """
    print(f"[fast] {message.text}")

```


---

**Previous**: [Build](../relational-databases/build.md) | **Next**: [Agentic AI > Build](../agentic-ai/build.md)
