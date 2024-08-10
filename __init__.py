import websockets
import os
import json
import asyncio

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

from config import Config, logger

websocket_connection = None

instance = Communication

class LagrangeClient(Lagrange):
    def get_client(self):
        return self.client

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
    logger.login.error(f"Kicked by Server: [{event.title}] {event.tips}")
    await client.stop()

lag = LagrangeClient(
    uin = Config.uin,
    protocol = Config.protocol,
    sign_url = Config.sign_server
)

async def process(client: Client, data: dict) -> dict:
    echo = data.get("echo")
    action = data.get("action")
    if not hasattr(instance, action):
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    params = data.get("params")
    method = getattr(instance, action)
    resp = await method(client=lag.get_client(), echo=echo, **params)
    return resp

async def connect():
    global websocket_connection
    uri = Config.ws_url
    while True:
        try:
            async with websockets.connect(uri, extra_headers={"X-Self-Id": str(Config.uin)}) as websocket:
                websocket_connection = websocket
                logger.onebot.info("WebSocket Established")
                while True:

                    try:
                        rec = await websocket.recv()
                        rec = json.loads(rec)

                        try:
                            rply = await process(lag.get_client(), rec)
                            await websocket.send(json.dumps(rply, ensure_ascii=False))
                        except Exception as e:
                            logger.onebot.error(f"Error while processing message: {e}")
                        
                    except websockets.exceptions.ConnectionClosed:
                        logger.onebot.warning("WebSocket Closed")
                        break
                    except Exception as e:
                        logger.onebot.error(f"Unhandled Exception in message handling: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.onebot.warning("WebSocket Connection Closed, retrying...")
            continue
        except websockets.exceptions.ConnectionClosedError as e:
            logger.onebot.error(f"WebSocket Connection Closed: {e}")
            continue
        except ConnectionRefusedError:
            logger.onebot.error("Connection Refused, retrying...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.onebot.error(f"Unhandled Exception: {e}")
        await asyncio.sleep(5)

        
lag.log.set_level(Config.log_level)
lag.subscribe(GroupMessage, msg_handler)
lag.subscribe(ServerKick, handle_kick)

async def main():
    task_lgr = asyncio.create_task(lag.run())
    task_ws = asyncio.create_task(connect())
    
    await asyncio.gather(task_lgr, task_ws)

asyncio.run(main())