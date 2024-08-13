from lagrange.client.client import Client

from lagrange.client.events.group import (
    GroupMessage
)
from lagrange.client.events.friend import (
    FriendMessage
)

from onebot.event.MessageEvent import (
    GroupMessageSender,
    GroupMessageEvent,
    PrivateMessageEvent
)
from onebot.utils.message_chain import MessageConverter
from onebot.uin import get_uid_by_uin, uid_dict

from config import Config

import json
import ws

async def GroupMessageEventHandler(client: Client, event: GroupMessage):
    sender_uid = get_uid_by_uin(event.uin)
    if not sender_uid:
        uid_dict[event.uin] = event.uid
    if ws.websocket_connection:
        msgcvt = MessageConverter(client)
        content = msgcvt.convert_to_segments((event.msg_chain))
        user_info = await client.get_user_info(event.uid)
        member_info = await client.get_grp_member_info(event.grp_id, event.uid)
        member_info = member_info.body[0]
        group_owner = not member_info.is_admin and member_info.permission == 2
        group_admin = member_info.is_admin
        if group_owner:
            role = "owner"
        elif group_admin:
            role = "admin"
        else:
            role = "member"
        sex = user_info.sex.name if user_info.sex.name != "notset" else "unknown"
        formated_event = GroupMessageEvent(
            message_id=event.seq,
            time=event.time, 
            group_id=event.grp_id, 
            user_id=event.uin, 
            self_id=Config.uin, 
            raw_message=event.msg, 
            message="".join(str(i) for i in content),
            sender=GroupMessageSender(
                user_id=event.uin,
                nickname=user_info.name,
                sex=sex,
                area=f"{user_info.country} {user_info.province} {user_info.city}",
                level=str(member_info.level.num),
                role=role
            )
        )
        await ws.websocket_connection.send(
            json.dumps(
                msgcvt.convert_to_dict(formated_event),
                ensure_ascii=False)
            )

async def PrivateMessageEventHandler(client: Client, event: FriendMessage):
    sender_uid = get_uid_by_uin(event.from_uin)
    receiver_uid = get_uid_by_uin(event.to_uin)
    if not sender_uid:
        uid_dict[event.from_uin] = event.from_uid
    if not receiver_uid:
        uid_dict[event.to_uin] = event.to_uid
    if ws.websocket_connection:
        msgcvt = MessageConverter(client)
        content = msgcvt.convert_to_segments((event.msg_chain))
        formated_event = PrivateMessageEvent(
            message_id=event.msg_id,
            time=event.timestamp, 
            group_id=0, 
            user_id=event.from_uin, 
            self_id=event.to_uin, 
            raw_message=event.msg, 
            message="".join(str(i) for i in content)
        )
        await ws.websocket_connection.send(
            json.dumps(
                msgcvt.convert_to_dict(formated_event),
                ensure_ascii=False)
            )