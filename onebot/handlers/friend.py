from typing import Any
from datetime import datetime

from lagrange.client.client import Client
from lagrange.client.events.friend import (
    FriendDeleted,
    FriendMessage,
    FriendRecall,
    FriendRequest
)

from onebot.utils.message_chain import MessageConverter
from onebot.utils.message import generate_message_id
from onebot.utils.database import db
from onebot.utils.datamodels import MessageEvent
from onebot.cache import get_user_info

from onebot.event.MessageEvent import (
    PrivateMessageEvent
)
from onebot.event.NoticeEvent import (
    FriendRecallNoticeEvent,
    FriendAddNoticeEvent,
    FriendDeletedNoticeEvent
)
from onebot.event.RequestEvent import (
    FriendRequestEvent
)

from config import logger

from .decorator import init_handler

@init_handler
async def PrivateMessageEventHandler(client: Client, converter: MessageConverter, event: FriendMessage):
    if event.msg.startswith("[json"):
        return
    content = await converter.convert_to_segments(event.msg_chain, "friend")
    message_id = generate_message_id(event.from_uin, event.seq)
    logger.onebot.info(
        f"Received message ({message_id}/{event.seq}) from friend ({event.from_uin})[({event.from_uid})]: {event.msg}"
    )
    record_data = MessageEvent(
        msg_id=message_id,
        uid=event.from_uid,
        seq=event.seq,
        uin=event.from_uin,
        msg=event.msg,
        msg_chain=[
            segment.__dict__
            for segment
            in (
                await converter.convert_to_segments(
                    event.msg_chain,
                    "friend",
                    uid=event.from_uid
                )
            )
        ]
    )
    db.save(record_data)
    return [
        PrivateMessageEvent(
            message_id=message_id,
            time=event.timestamp,
            user_id=event.from_uin,
            self_id=event.to_uin,
            raw_message=event.msg,
            message="".join(str(i) for i in content)
        )
    ]

@init_handler
async def FriendRecallEventHandler(client: Client, converter: MessageConverter, event: FriendRecall):
    uin = event.from_uin
    seq = event.seq
    message: MessageEvent | Any = db.where_one(MessageEvent(), "uin = ? AND seq = ?", uin, seq, default=None)
    if message is None:
        return
    return [
        FriendRecallNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            user_id=uin,
            message_id=message.msg_id
        )
    ]

@init_handler
async def FriendRequestEventHandler(client: Client, converter: MessageConverter, event: FriendRequest):
    flag = event.from_uid # 想不到吧 `uid`当`flag`.jpg
    uin = get_user_info(event.from_uid)
    if uin is None:
        return
    return [
        FriendRequestEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            user_id=uin,
            comment=event.message,
            flag=flag
        ),
        FriendAddNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            user_id=uin
        )
    ]

@init_handler
async def FriendDeletedEventHandler(client: Client, converter: MessageConverter, event: FriendDeleted):
    uin = get_user_info(event.from_uid)
    if uin is None:
        return
    return [
        FriendDeletedNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            user_id=uin
        )
    ]
