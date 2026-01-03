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
