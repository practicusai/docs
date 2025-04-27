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
