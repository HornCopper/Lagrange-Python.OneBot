from typing import Optional

from lagrange.client.client import Client
from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall
)
from lagrange.client.events.friend import (
    FriendMessage
)

from onebot.event.MessageEvent import (
    GroupMessageSender,
    GroupMessageEvent,
    PrivateMessageEvent,
    GroupDecreaseEvent,
    GroupRecallEvent
)
from onebot.utils.random import generate_message_id
from onebot.utils.database import db
from onebot.utils.datamodels import (
    MessageEvent
)
from onebot.utils.message_chain import MessageConverter
from onebot.cache import get_info

from config import Config

import json
import ws

async def GroupMessageEventHandler(client: Client, event: GroupMessage):
    if ws.websocket_connection:
        msgcvt = MessageConverter(client)
        content = await msgcvt.convert_to_segments(event.msg_chain, "grp", group_id=event.grp_id)
        message_id = generate_message_id()
        if Config.ignore_self and event.uin == client.uin:
            return
        event_content = event.__dict__
        record_data = MessageEvent(
            msg_id=message_id,
            msg_chain=(json.dumps(element.__dict__, ensure_ascii=False) for element in event_content.pop("msg_chain")),
            **(event_content)
        )
        db.save(record_data)
        formated_event = GroupMessageEvent(
            message_id=message_id,
            time=event.time, 
            group_id=event.grp_id, 
            user_id=event.uin, 
            self_id=client.uin, 
            raw_message=event.msg, 
            message="".join(str(i) for i in content),
            sender=GroupMessageSender(
                user_id=event.uin,
                nickname=event.nickname
            )
        )
        await ws.websocket_connection.send(
            json.dumps(
                msgcvt.convert_to_dict(formated_event),
                ensure_ascii=False)
            )

async def PrivateMessageEventHandler(client: Client, event: FriendMessage):
    if ws.websocket_connection:
        msgcvt = MessageConverter(client)
        content = await msgcvt.convert_to_segments(event.msg_chain, "friend")
        message_id = generate_message_id()
        event_content = event.__dict__
        record_data = MessageEvent(
            msg_id=message_id,
            uid=event.from_uid,
            seq=event.seq,
            uin=event.from_uin,
            msg=event.msg,
            msg_chain=(json.dumps(element.__dict__, ensure_ascii=False) for element in event_content.pop("msg_chain"))
        )
        db.save(record_data)
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
        
async def GroupRecallEventHandler(client: Client, event: GroupRecall):
    if ws.websocket_connection:
        msgcvt = MessageConverter(client)
        uin = get_info(event.uid)
        message_event: Optional[MessageEvent] = db.where_one(MessageEvent(), "seq = ? AND grp_id = ?", event.seq, event.grp_id, default=None)
        if message_event is None:
            return
        formated_event = GroupRecallEvent(
            self_id = client.uin,
            group_id = event.grp_id,
            operator_id = uin,
            user_id = message_event.uin,
            message_id = message_event.msg_id
        )
        await ws.websocket_connection.send(
            json.dumps(
                msgcvt.convert_to_dict(formated_event),
                ensure_ascii=False)
            )