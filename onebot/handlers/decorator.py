from functools import wraps

from lagrange.client.client import Client
from lagrange.utils.httpcat import HttpCat

from onebot.event.ManualEvent import Event
from onebot.utils.message_chain import MessageConverter

from config import Config

import json
import reserved_websocket
import forward_websocket

def init_handler(func):
    @wraps(func)
    async def wrapper(client: Client, *args, **kwargs):
        converter = MessageConverter(client)
        data: list[Event] = await func(client, converter, *args, **kwargs)
        if data:
            if reserved_websocket.websocket_connection:
                for event in data:
                    await reserved_websocket.websocket_connection.send(
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
            for event in data:
                await forward_websocket.forward_websocket_manager.send_message(
                    json.dumps(
                        converter.convert_to_dict(event),
                        ensure_ascii=False
                    )
                )
    return wrapper
