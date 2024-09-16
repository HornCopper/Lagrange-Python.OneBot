from typing import Optional
from functools import wraps

from lagrange.client.client import Client
from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall,
    GroupMemberQuit,
    GroupMemberJoinRequest
)
from lagrange.client.events.friend import (
    FriendMessage
)
from lagrange.pb.service.group import (
    FetchGrpRspBody
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
            converter.convert_to_dict(formated_event),
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
            converter.convert_to_dict(formated_event),
            ensure_ascii=False
        )
    )

@init_handler   
async def GroupDecreaseEventHandler(client: Client, converter: MessageConverter, event: GroupMemberQuit):
    sub_type = "kick" if event.exit_type == 3 else "leave"
    if event.uid == client.uid:
        sub_type = sub_type + "_me"
    operator_id = get_info(event.operator_uid)
    if operator_id == None:
        operator_id = 0
    formated_event = GroupDecreaseNoticeEvent(
        self_id = client.uin,
        sub_type = sub_type,
        group_id = event.grp_id,
        operator_id = operator_id,
        user_id = event.uin
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formated_event),
            ensure_ascii=False
        )
    )
    
@init_handler
async def GroupRecallEventHandler(client: Client, converter: MessageConverter, event: GroupRecall):
    uin = get_info(event.uid)
    message_event: Optional[MessageEvent] = db.where_one(MessageEvent(), "seq = ? AND grp_id = ?", event.seq, event.grp_id, default=None)
    if message_event is None:
        return
    formated_event = GroupRecallNoticeEvent(
        self_id = client.uin,
        group_id = event.grp_id,
        operator_id = uin,
        user_id = message_event.uin,
        message_id = message_event.msg_id
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formated_event),
            ensure_ascii=False
        )
    )

@init_handler
async def GroupRequestEventHandler(client: Client, converter: MessageConverter, event: GroupMemberJoinRequest):
    requests = await client.fetch_grp_request()
    request: FetchGrpRspBody = requests.requests[0]
    formated_event = GroupRequestEvent(
        self_id = client.uin,
        sub_type = "add" if event.uid != client.uid else "invite",
        group_id = event.grp_id,
        user_id = get_info(request.target.uid),
        comment = request.comment,
        flag = str(request.seq) + "-" + str(request.group.grp_id) + "-" + str(request.event_type) 
    )
    await ws.websocket_connection.send(
        json.dumps(
            converter.convert_to_dict(formated_event),
            ensure_ascii=False
        )
    )