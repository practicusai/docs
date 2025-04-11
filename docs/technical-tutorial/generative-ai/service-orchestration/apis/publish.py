import practicuscore as prt
from pydantic import BaseModel


mq_conn = None

mq_user = "guest"
mq_pwd = "guest"
mq_host = "prt-mq-default"
mq_vhost = ""  # Recommended for fine-grained security
mq_conn_str = f"amqp://{mq_user}:{mq_pwd}@{mq_host}/{mq_vhost}"

# Assuming queue(s) and binding(s) are already configured.
mq_config = prt.MQConfig(
    conn_str=mq_conn_str,
    exchange="my-first-exchange",
)


class MyMsg(BaseModel):
    text: str


async def connect():
    global mq_conn
    mq_conn = await prt.mq.connect(mq_config)


@prt.apps.api("/publish")
async def publish(payload: MyMsg, **kwargs):
    if mq_conn is None:
        await connect()

    await prt.mq.publish(mq_conn, payload)

    return {"ok": True}
