from datetime import datetime
from pathlib import Path
from typing import Union, Literal, List, Optional

from lagrange.client.client import Client, BotFriend
from lagrange.client.message.elems import Text
from lagrange.pb.service.group import GetGrpMemberInfoRspBody

from onebot.utils.message_segment import MessageSegment
from onebot.utils.random import generate_message_id
from onebot.utils.message_chain import MessageConverter
from onebot.utils.database import db
from onebot.utils.datamodels import MessageEvent
from onebot.event.ManualEvent import Anonymous
from onebot.event.MessageEvent import GroupMessageSender
from onebot.cache import get_info

import uuid
import httpx
import json

from config import Config

from .ManualInfo import GroupInfo

class Communication:
    def __init__(self, client: Client):
        self.client = client
        self.message_converter = MessageConverter(self.client)
    
    async def send_group_msg(self, group_id: int, message: Union[list, str], echo: str, user_id: int = 0) -> dict:
        if isinstance(message, list):
            message = self.message_converter.parse_message(message, MessageSegment)
            message_ = await self.message_converter.convert_to_elements(message, group_id)
        elif isinstance(message, str):
            message_ = [Text(message)]
            message = message_
        seq = await self.client.send_grp_msg(msg_chain=message_, grp_id=group_id)
        message_id = generate_message_id()
        msg_content = MessageEvent(
            msg_id = message_id,
            uin = self.client.uin,
            uid = self.client.uid,
            seq = seq,
            grp_id = group_id,
            msg_chain = (json.dumps(element.__dict__, ensure_ascii=False) for element in message)
        )
        db.save(msg_content)
        return {"status": "ok", "retcode": 0, "data": {"message_id": message_id}, "echo": echo}
    
    async def send_private_msg(self, user_id: int, message: Union[list, str], echo: str, group_id: int = 0) -> dict:
        uid = get_info(user_id)
        if not uid:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        if isinstance(message, list):
            message = self.message_converter.parse_message(message, MessageSegment)
            message_ = await self.message_converter.convert_to_elements(message, message, uid)
        elif isinstance(message, str):
            message_ = [Text(message)]
        seq = await self.client.send_friend_msg(msg_chain=message_, uid=uid)
        message_id = generate_message_id()
        msg_content = MessageEvent(
            msg_id = message_id,
            uin = self.client.uin,
            uid = self.client.uid,
            seq = seq,
            grp_id = group_id,
            msg_chain = (json.dumps(element.__dict__, ensure_ascii=False) for element in message)
        )
        db.save(msg_content)
        return {"status": "ok", "retcode": 0, "data": {"message_id": seq}, "echo": echo}
    
    async def send_msg(
            self, 
            user_id: int, 
            message_type: Literal["group", "private"], 
            message: Union[list, str],
            echo: str,
            group_id: int = 0
        ) -> dict:
        method = getattr(self, f"send_{message_type}_msg")
        return await method(user_id=user_id, message=message, group_id=group_id, echo=echo)
    
    async def get_group_info(self, group_id: int, echo: str, no_cache: bool = False) -> dict:
        if no_cache:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
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

    async def delete_msg(self, message_id: int, echo: str) -> dict:
        message_event: Optional[MessageEvent] = db.where_one(MessageEvent(), "msg_id = ?", message_id, default=None)
        if message_event is None:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        if message_event.grp_id == 0:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        group_id = message_event.grp_id
        seq = message_event.seq
        await self.client.recall_grp_msg(group_id, seq)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def get_msg(self, message_id: int, echo: str) -> dict:
        message_event: Optional[MessageEvent] = db.where_one(MessageEvent(), "msg_id = ?", message_id, default=None)
        if message_event is None:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        data = {
            "message_type": "private",
            "message_id": message_event.msg_id,
            "real_id": message_event.msg_id,
            "sender": GroupMessageSender(
                user_id = message_event.uin,
                nickname = message_event.nickname
            ).model_dump()
        }
        return {"status": "failed", "retcode": 0, "data": data, "echo": echo}
    
    async def get_forward_msg(self, id: str, echo: str) -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}

    async def send_like(self, user_id: int, times: int, echo: str) -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool, echo: str) -> dict:
        await self.client.kick_grp_member(group_id, user_id, reject_add_request)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def set_group_ban(self, group_id: int, user_id: int, duration: int, echo: str) -> dict:
        await self.client.set_mute_member(group_id, user_id, duration)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def set_group_anonymous_ban(self, group_id: int, anonymous: Anonymous, anonymous_flag: str, flag: str, duration: int, echo: str) -> dict:
        # Not Impl Forever
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def set_group_whole_ban(self, group_id: int, enable: bool, echo: str) -> dict:
        await self.client.set_mute_grp(group_id, enable)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def set_group_admin(self, group_id: int, user_id: int, enable: bool, echo: str) -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def set_group_anonymous(self, group_id: int, enable: bool, echo: str) -> dict:
        # Not Impl Forever
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def set_group_card(self, group_id: int, user_id: int, card: str, echo: str) -> dict:
        uid = get_info(user_id)
        if not uid:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        await self.client.rename_grp_member(group_id, uid, card)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def set_group_name(self, group_id: int, group_name: str, echo: str) -> dict:
        await self.client.rename_grp_name(group_id, group_name)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}

    async def set_group_leave(self, group_id: int, echo: str, is_dismiss: bool = False) -> dict:
        if is_dismiss:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo} # Not Impl
        await self.client.leave_grp(group_id)
        return {"status": "ok", "retcode": 0, "data": None, "echo": echo}
    
    async def set_group_special_title(self, group_id: int, special_title: str, echo: str, duration: int = -1) -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def set_friend_add_request(self, flag: str, approve: bool, echo: str, remark: str = "") -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}

    async def set_group_add_request(
            self, 
            echo: str,
            flag: str = "", 
            sub_type: Literal["add", "invite"] = "",
            approve: bool = False, 
            reason: str = ""
        ) -> dict:
        # Working
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def get_login_info(self, echo: str) -> dict:
        info = await self.client.get_user_info(self.client.uid)
        return {"status": "ok", "retcode": 0, "data": {"user_id": self.client.uin, "nickname": info.name}, "echo": echo}
    
    async def get_stranger_info(self, user_id: int, echo: str, no_cache: bool = False) -> dict:
        uid = get_info(user_id)
        if not uid:
            return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        info = await self.client.get_user_info(uid)
        sex = info.sex.name if info.sex.name != "notset" else "unknown"
        today = datetime.today()
        birthday = info.birthday
        age = today.year - birthday.year
        if (today.month, today.day) < (birthday.month, birthday.day):
            age -= 1
        return {"status": "ok", "retcode": 0, "data": {"user_id": user_id, "nickname": info.name, "sex": sex, "age": age}, "echo": echo}
    
    async def get_friend_list(self, echo: str) -> dict:
        data = self.client.get_friend_list()
        friend_list = []
        for friend in data:
            friend: BotFriend
            friend_list.append(
                {
                    "user_id": friend.uin,
                    "nickname": friend.nickname,
                    "remark": friend.remark
                }
            )
        return {"status": "ok", "retcode": 0, "data": friend_list, "echo": echo}
    
    async def get_group_member_info(self, group_id: int, user_id: int, echo: str, no_cache: bool = False, uid: str = "") -> dict:
        if uid == "":
            uid = get_info(user_id)
            if not uid:
                return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
        member_info = await self.client.get_grp_member_info(group_id, uid)
        person_info = await self.get_stranger_info(user_id, echo)
        group_owner = not member_info.body[0].is_admin and member_info.body[0].permission == 2
        group_admin = member_info.body[0].is_admin
        if group_owner:
            role = "owner"
        elif group_admin:
            role = "admin"
        else:
            role = "member"
        return {
            "status": "ok", 
            "retcode": 0, 
            "data": {
                "group_id": group_id, 
                "card": "", 
                "join_time": member_info.body[0].joined_time,
                "last_sent_time": member_info.body[0].last_seen,
                "level": str(member_info.body[0].level.num),
                "role": role,
                "unfriendly": False,
                "title": "",
                "title_expire_time": 0,
                "card_changeable": True,
                **(person_info["data"])
            }, 
            "echo": echo
        }
    
    async def get_group_member_list(self, group_id: int, echo: str, no_cache: bool = False) -> dict:
        group_members_resp: List[GetGrpMemberInfoRspBody] = []
        group_members_data = []
        while True:
            rsp = await self.client.get_grp_members()
            if len(rsp.body) == 0:
                break
            group_members_resp.append(rsp.body)
        for group_member_info_resp in group_members_resp:
            group_member_info_resp: GetGrpMemberInfoRspBody
            group_owner = not group_member_info_resp.is_admin and group_member_info_resp.permission == 2
            group_admin = group_member_info_resp.is_admin
            if group_owner:
                role = "owner"
            elif group_admin:
                role = "admin"
            else:
                role = "member"
            person_info_resp = await self.get_stranger_info(echo=echo, uid=group_member_info_resp.account.uid)
            group_members_data.append(
                {
                    "group_id": group_id, 
                    "card": "", 
                    "join_time": group_member_info_resp.joined_time,
                    "last_sent_time":group_member_info_resp.last_seen,
                    "level": str(group_member_info_resp.level.num),
                    "role": role,
                    "unfriendly": False,
                    "title": "",
                    "title_expire_time": 0,
                    "card_changeable": True,
                    **(person_info_resp["data"])
                }
            )
        return {"status": "ok", "retcode": 0, "data": group_members_data, "echo": echo}
    
    async def get_group_honor_info(
            self, 
            group_id: int, 
            echo: str, 
            type: Literal["talkative", "performer", "legend", "strong_newbie", "emotion", "all"] = "all", 
        ) -> dict:
        # Not Impl
        return {"status": "failed", "retcode": -1, "data": None, "echo": echo}
    
    async def get_image(self, file: str, echo: str) -> dict:
        file_format, file_content = await self._get_image_type(file)
        with open(f"./onebot/images/{self._get_uuid()}.{file_format}", "wb") as img:
            img.write(file_content)
            return Path(f"./onebot/images/{self._get_uuid()}.{file_format}").resolve()

    def _get_uuid(self) -> dict:
        return str(uuid.uuid1()).replace("-", "")

    async def _get_image_type(self, url) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            file_signature = response.content[:8]
            if file_signature.startswith(b'\x89PNG\r\n\x1a\n'):
                return "png", response.content
            elif file_signature.startswith(b'\xff\xd8'):
                return "jpg", response.content
            elif file_signature.startswith(b'BM'):
                return "bmp", response.content
            elif file_signature[:6] in (b'GIF87a', b'GIF89a'):
                return "gif", response.content
            else:
                raise ValueError("Unknown Type of Image!")