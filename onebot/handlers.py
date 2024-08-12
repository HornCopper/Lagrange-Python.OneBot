from lagrange.client.client import Client

from lagrange.client.events.group import (
    GroupMessage
)
from lagrange.client.events.friend import (
    FriendMessage
)

from onebot.event.MessageEvent import (
    GroupMessageEvent,
    PrivateMessageEvent
)
from onebot.utils.message_chain import ms_format, ctd
from onebot.uin import get_uid_by_uin, uid_dict

from config import Config

import json
import ws

async def GroupMessageEventHandler(client: Client, event: GroupMessage):
    if ws.websocket_connection:
        content = ms_format(event.msg_chain)
        formated_event = GroupMessageEvent(
            message_id=event.seq,
            time=event.time, 
            group_id=event.grp_id, 
            user_id=event.uin, 
            self_id=Config.uin, 
            raw_message=event.msg, 
            message="".join(str(i) for i in content)
        )
        await ws.websocket_connection.send(
            json.dumps(
                ctd(formated_event),
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
        content = ms_format(event.msg_chain)
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
                ctd(formated_event),
                ensure_ascii=False)
            )