from typing import Any
from functools import wraps

from lagrange.client.client import Client
from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall,
    GroupMemberQuit,
    GroupInvite,
    GroupMemberJoinRequest
)
from lagrange.client.events.friend import (
    FriendMessage
)
from onebot.event.MessageEvent import (
    GroupMessageSender,
    GroupMessageEvent,
    PrivateMessageEvent
)
from onebot.event.NoticeEvent import (
    GroupDecreaseNoticeEvent,
    GroupRecallNoticeEvent
)
from onebot.event.RequestEvent import (
    GroupRequestEvent
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

def init_handler(func):
    @wraps(func)
    async def wrapper(client: Client, *args, **kwargs):
        if not ws.websocket_connection:
            return
        converter = MessageConverter(client)
        return await func(client, converter, *args, **kwargs)
    return wrapper

@init_handler
async def GroupMessageEventHandler(client: Client, converter: MessageConverter, event: GroupMessage):
    content = await converter.convert_to_segments(event.msg_chain, "grp", group_id=event.grp_id)
    message_id = generate_message_id(event.grp_id, event.seq)
    if Config.ignore_self and event.uin == client.uin:
        return
    event_content = event.__dict__
    record_data = MessageEvent(
        msg_id=message_id,
        msg_chain=list([json.dumps(element.__dict__, ensure_ascii=False) for element in event_content.pop("msg_chain")]),
        **(event_content)
    )
    db.save(record_data)
    formatted_event = GroupMessageEvent(
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
            converter.convert_to_dict(formatted_event),
            ensure_ascii=False
        )
    )

@init_handler
async def PrivateMessageEventHandler(client: Client, converter: MessageConverter, event: FriendMessage):
    if event.msg.startswith("[json"):
        return
    content = await converter.convert_to_segments(event.msg_chain, "friend")
    message_id = generate_message_id(event.from_uin, event.seq)
    event_content = event.__dict__
    record_data = MessageEvent(
        msg_id=message_id,
        uid=event.from_uid,
        seq=event.seq,
        uin=event.from_uin,
        msg=event.msg,
        msg_chain=list([json.dumps(element.__dict__, ensure_ascii=False) for element in event_content.pop("msg_chain")])
    )
    db.save(record_data)
    formatted_event = PrivateMessageEvent(
        message_id=event.msg_id,
        time=event.timestamp,
        user_id=event.from_uin, 
        self_id=event.to_uin, 
        raw_message=event.msg, 
        message="".join(str(i) for i in content)
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formatted_event),
            ensure_ascii=False
        )
    )

@init_handler   
async def GroupDecreaseEventHandler(client: Client, converter: MessageConverter, event: GroupMemberQuit):
    if event.is_kicked_self:
        sub_type = "kick_me"
    elif event.is_kicked and not event.is_kicked_self:
        sub_type = "kick"
    else:
        sub_type = "leave"
    correct_operator_uid = ''.join([char for char in event.operator_uid.split("\n")[2].split(" ")[0] if char.isprintable()])
    print(event.operator_uid)
    operator_id = get_info(correct_operator_uid)
    if operator_id == None:
        operator_id = 0
    formatted_event = GroupDecreaseNoticeEvent(
        self_id = client.uin,
        sub_type = sub_type,
        group_id = event.grp_id,
        operator_id = int(operator_id),
        user_id = event.uin
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formatted_event),
            ensure_ascii=False
        )
    )
    
@init_handler
async def GroupRecallEventHandler(client: Client, converter: MessageConverter, event: GroupRecall):
    uin = get_info(event.uid)
    if not uin:
        return
    message_event: MessageEvent | Any = db.where_one(MessageEvent(), "seq = ? AND grp_id = ?", event.seq, event.grp_id, default=None)
    if message_event is None:
        return
    formatted_event = GroupRecallNoticeEvent(
        self_id = client.uin,
        group_id = event.grp_id,
        operator_id = int(uin),
        user_id = message_event.uin,
        message_id = message_event.msg_id
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formatted_event),
            ensure_ascii=False
        )
    )

@init_handler
async def GroupRequestEventHandler(client: Client, converter: MessageConverter, event: GroupInvite | GroupMemberJoinRequest):
    latest_request = (await client.fetch_grp_request()).requests[0]
    if event.invitor_uid is None:
        return
    uin = get_info(event.invitor_uid)
    if not uin:
        return
    sub_type = "invite" if isinstance(event, GroupInvite) else "add"
    formatted_event = GroupRequestEvent(
        self_id = client.uin,
        sub_type = sub_type,
        group_id = event.grp_id,
        user_id = int(uin),
        comment = "" if isinstance(event, GroupInvite) else str(event.answer),
        flag = str(event.grp_id) + "-" + str(latest_request.seq) + "-" + str(latest_request.event_type) + "-" + sub_type
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formatted_event),
            ensure_ascii=False
        )
    )