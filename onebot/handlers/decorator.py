from functools import wraps

from lagrange.client.client import Client
from lagrange.utils.httpcat import HttpCat

from onebot.event.ManualEvent import Event
from onebot.utils.message_chain import MessageConverter

from config import Config

import json
import ws

def init_handler(func):
    @wraps(func)
    async def wrapper(client: Client, *args, **kwargs):
        converter = MessageConverter(client)
        data: list[Event] = await func(client, converter, *args, **kwargs)
        if data:
            if ws.websocket_connection:
                for event in data:
                    await ws.websocket_connection.send(
                        json.dumps(
                            converter.convert_to_dict(event),
                            ensure_ascii=False
                        )
                    )
            if Config.http_post_url.startswith("http"):
                headers = {
                    "Content-Type": "application/json",
                    "X-Self-ID": str(client.uin)
                }
                for event in data:
                    await HttpCat.request(
                        "POST",
                        Config.http_post_url,
                        headers,
                        json.dumps(
                            converter.convert_to_dict(event),
                            ensure_ascii=False
                        ).encode("utf-8")
                    )
    return wrapper
