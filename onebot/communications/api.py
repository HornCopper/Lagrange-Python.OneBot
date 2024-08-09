from nonebot.adapters.onebot.v11 import MessageSegment
from lagrange.client.client import Client
from lagrange.client.message.elems import Text
from onebot.utils.message_chain import format, ms_unformat

from typing import Union, Literal

from .ManualInfo import GroupInfo

class Communication:
    def __init__(self):
        ...
    
    @staticmethod
    async def send_group_msg(client: Client, group_id: int, message: Union[list, str], echo: str, user_id: int = 0) -> dict:
        if isinstance(message, list):
            message = format(message, MessageSegment)
            message = ms_unformat(message)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await client.send_grp_msg(msg_chain=message, grp_id=group_id)
        return {"status": "ok", "retcode": 0, "data": {"message_id": message_id}, "echo": echo}
    
    @staticmethod
    async def send_private_msg(client: Client, user_id: int, message: Union[list, str], echo: str) -> dict:
        if isinstance(message, list):
            message = format(message, MessageSegment)
            message = ms_unformat(message)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await client.send_friend_msg(msg_chain=message, uid=user_id)
        return {"status": "ok", "retcode": 0, "data": {"message_id": message_id}, "echo": echo}
    
    @staticmethod
    async def send_msg(client: Client, user_id: int, group_id: int, message_type: Literal["group", "private"], message: Union[list, str], echo: str) -> dict:
        method = getattr(Communication, f"send_{message_type}_msg")
        return await method(client=client, user_id=user_id, message=message, group_id=group_id, echo=echo)
    
    @staticmethod
    async def get_group_info(client: Client, group_id: int, cache: bool, echo: str) -> dict:
        data = await Communication.get_group_list(client=client)
        for group in data["data"]:
            if group_id == group["group_id"]:
                return {"status": "ok", "retcode": 0, "data": group, "echo": echo}
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}

    @staticmethod
    async def get_group_list(client: Client, echo: str) -> dict:
        data = await client.get_grp_list()
        groups = []
        for grp in data.grp_list:
            group_data = GroupInfo(
                group_id=grp.grp_id,
                group_name=grp.info.grp_name,
                member_count=grp.info.now_members,
                max_member_count=grp.info.max_members
            ).__dict__
            groups.append(group_data)
        return {"status": "ok", "retcode": 0, "data": groups, "echo": echo}