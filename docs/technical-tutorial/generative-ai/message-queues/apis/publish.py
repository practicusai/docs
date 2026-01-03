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
