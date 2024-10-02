from functools import wraps

from lagrange.client.client import Client

from onebot.utils.message_chain import MessageConverter

import ws

def init_handler(func):
    @wraps(func)
    async def wrapper(client: Client, *args, **kwargs):
        if not ws.websocket_connection:
            return
        converter = MessageConverter(client)
        return await func(client, converter, *args, **kwargs)
    return wrapper