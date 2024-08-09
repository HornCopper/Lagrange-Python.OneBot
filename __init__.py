import websockets
import os
import json
import asyncio
import threading
import signal

config_default = """# Lagrange Python (OneBot V11) Configuration

uin: ""
# Bot QQ号 使用扫码登录

protocal: ""
# 登录协议 推荐使用Linux（默认）

signserver: ""
# SignServer 地址 不可使用`Android`的`QSign`

ws_url: ""
# 反向 WebSocket 地址
"""

if not os.path.exists("./config.yml"):
    print("The configuration file does not exist, please edit it, it has been created for you in current directory.")
    with open("./config.yml", "w", encoding="utf8") as f:
        f.write(config_default)
    os._exit(0)

from lagrange import Lagrange
from lagrange.client.client import Client
from lagrange.client.events.group import GroupMessage
from lagrange.client.events.service import ServerKick

from onebot.communications.api import Communication
from onebot.event.MessageEvent import GroupMessageEvent
from onebot.utils.message_chain import ms_format, ctd

from config import Config

websocket_connection = None

instance = Communication

async def msg_handler(client: Client, event: GroupMessage):
    if websocket_connection:
        content = ms_format(event.msg_chain)
        formated_event = GroupMessageEvent(
            message_id=event.seq,
            time=event.time, 
            group_id=event.grp_id, 
            user_id=event.uin, 
            self_id=int(Config.uin), 
            raw_message=event.msg, 
            message="".join(str(i) for i in content)
        )
        await websocket_connection.send(
            json.dumps(
                ctd(formated_event),
                ensure_ascii=False)
            )
    else:
        ...

async def handle_kick(client: "Client", event: "ServerKick"):
    print(f"Kicked by Server: [{event.title}] {event.tips}")
    await client.stop()

lag = Lagrange(
    uin = Config.uin,
    protocol = Config.protocal,
    sign_url = Config.signserver
)

async def connect():
    global websocket_connection
    uri = Config.ws_url
    while True:
        try:
            async with websockets.connect(uri, extra_headers={"X-Self-Id": str(Config.uin)}) as websocket:
                websocket_connection = websocket
                print("WebSocket Established")

                while True:
                    try:
                        response = await websocket.recv()
                        response = json.loads(response)
                        print(response)
                        params = response.get("params")
                        action = response.get("action")
                        method = getattr(instance, action)
                        resp = await method(client=client, **params)
                        await websocket.send(json.dumps(resp, ensure_ascii=False))
                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket Closed")
                        break
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket Connection Closed, retrying...")

        await asyncio.sleep(5)
        
lag.log.set_level("DEBUG")
lag.subscribe(GroupMessage, msg_handler)
lag.subscribe(ServerKick, handle_kick)

def run_websocket():
    asyncio.run(connect())

ws_thread = threading.Thread(target=run_websocket)
ws_thread.start()

def handle_sigint(signum, frame):
    print("KeyboardInterrupt")
    os._exit(0)

signal.signal(signal.SIGINT, handle_sigint)

lag.launch()