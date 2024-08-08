import asyncio
import os
import yaml

from lagrange import Lagrange
from lagrange.client.client import Client
from lagrange.client.events.group import GroupMessage
from lagrange.client.events.service import ServerKick
from lagrange.client.message.elems import At, Raw, Text

class config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = config(**value)
            setattr(self, key, value)

def yaml_to_class(yaml_str, cls):
    config_data = yaml.safe_load(yaml_str)
    return cls(**config_data)

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, "config.yml")

with open(yaml_file_path, "r", encoding="utf8") as f:
    Config = yaml_to_class(f.read(), config)

async def msg_handler(client: Client, event: GroupMessage):
    print(event)
    if event.msg.startswith("114514"):
        p = await client.send_grp_msg([Text("1919810")], event.grp_id)
        await asyncio.sleep(5)
        await client.recall_grp_msg(event.grp_id, p)
    elif event.msg.startswith("imgs"):
        await client.send_grp_msg(
            [
                await client.upload_grp_image(
                    open("98416427_p0.jpg", "rb"), event.grp_id
                )
            ],
            event.grp_id,
        )
    print(f"{event.nickname}({event.grp_name}): {event.msg}")


async def handle_kick(client: "Client", event: "ServerKick"):
    print(f"被服务器踢出：[{event.title}] {event.tips}")
    await client.stop()


lag = Lagrange(
    uin = Config.uin,
    protocol = Config.protocal,
    sign_url = Config.signserver
)
lag.log.set_level("DEBUG")
lag.subscribe(GroupMessage, msg_handler)
lag.subscribe(ServerKick, handle_kick)


lag.launch()