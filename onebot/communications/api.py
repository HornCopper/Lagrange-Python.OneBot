from lagrange.client.client import Client
from lagrange.client.message.elems import Text

from onebot.utils.message_segment import MessageSegment
from onebot.utils.message_chain import MessageConverter
from onebot.uin import get_uid_by_uin

from typing import Union, Literal

from .ManualInfo import GroupInfo

class Communication:
    def __init__(self, client: Client):
        self.client = client
        self.message_converter = MessageConverter(self.client)
    
    async def send_group_msg(self, group_id: int, message: Union[list, str], echo: str, user_id: int = 0) -> dict:
        if isinstance(message, list):
            message = self.message_converter.parse_message(message, MessageSegment)
            message = await self.message_converter.convert_to_elements(message, group_id)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await self.client.send_grp_msg(msg_chain=message, grp_id=group_id)
        return {"status": "ok", "retcode": 0, "data": {"message_id": message_id}, "echo": echo}
    
    async def send_private_msg(self, user_id: int, message: Union[list, str], echo: str, group_id: int = 0) -> dict:
        uid = get_uid_by_uin(user_id)
        if not uid:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        if isinstance(message, list):
            message = self.message_converter.parse_message(message, MessageSegment)
            message = await self.message_converter.convert_to_elements(self.client, message, uid)
        elif isinstance(message, str):
            message = [Text(message)]
        message_id = await self.client.send_friend_msg(msg_chain=message, uid=uid)
        return {"status": "ok", "retcode": 0, "data": {"message_id": message_id}, "echo": echo}
    
    async def send_msg(self, user_id: int, message_type: Literal["group", "private"], message: Union[list, str], echo: str, group_id: int = 0) -> dict:
        method = getattr(self, f"send_{message_type}_msg")
        return await method(user_id=user_id, message=message, group_id=group_id, echo=echo)
    
    async def get_group_info(self, group_id: int, cache: bool, echo: str) -> dict:
        data = await self.get_group_list(echo=echo)
        for group in data["data"]:
            if group_id == group["group_id"]:
                return {"status": "ok", "retcode": 0, "data": group, "echo": echo}
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}

    async def get_group_list(self, echo: str) -> dict:
        data = await self.client.get_grp_list()
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