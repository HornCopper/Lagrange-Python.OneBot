from nonebot.adapters.onebot.v11 import MessageSegment
from lagrange.client.client import Client
from lagrange.client.message.elems import Text
from onebot.utils.message_chain import format, ms_unformat

from typing import Union, Literal

class Communication:
    def __init__(self):
        ...
    
    @staticmethod
    async def send_group_msg(client: Client, group_id: int, message: Union[list, str]) -> dict:
        if isinstance(message, list):
            message = format(message, MessageSegment)
            message = ms_unformat(message)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await client.send_grp_msg(msg_chain=message, grp_id=group_id)
        return {"status": "ok", "retcode": "0", "data": {"message_id": message_id}}
    
    @staticmethod
    async def send_private_msg(client: Client, user_id: int, message: Union[list, str]) -> dict:
        if isinstance(message, list):
            message = format(message, MessageSegment)
            message = ms_unformat(message)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await client.send_friend_msg(msg_chain=message, uid=user_id)
        return {"status": "ok", "retcode": "0", "data": {"message_id": message_id}}
    
    @staticmethod
    async def send_msg(client: Client, user_id: int, group_id: int, message_type: Literal["group", "private"], message: Union[list, str]) -> dict:
        method = getattr(Communication, f"send_{message_type}_msg")
        return await method(client=client, user_id=user_id, message=message)