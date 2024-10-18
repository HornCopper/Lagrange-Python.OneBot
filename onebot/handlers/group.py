from typing import Any
from datetime import datetime

from lagrange.client.client import Client
from lagrange.client.events.group import (
    GroupMessage,
    GroupInvite,
    GroupMemberJoinRequest,
    GroupRecall,
    GroupMemberQuit,
    GroupNudge,
    GroupMuteMember,
    GroupMemberJoined,
    GroupMemberJoinedByInvite,
    GroupAdminChange
)

from onebot.utils.message_chain import MessageConverter
from onebot.utils.message import generate_message_id
from onebot.utils.database import db
from onebot.utils.datamodels import MessageEvent
from onebot.cache import get_user_info

from onebot.event.MessageEvent import (
    GroupMessageEvent, GroupMessageSender
)
from onebot.event.NoticeEvent import (
    GroupDecreaseNoticeEvent,
    GroupBanNoticeEvent,
    GroupRecallNoticeEvent,
    GroupPokeNotifyNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupAdminNoticeEvent
)
from onebot.event.RequestEvent import (
    GroupRequestEvent
)

from config import Config, logger

from .decorator import init_handler

@init_handler
async def GroupMessageEventHandler(client: Client, converter: MessageConverter, event: GroupMessage):
    content = await converter.convert_to_segments(event.msg_chain, "grp", group_id=event.grp_id)
    message_id = generate_message_id(event.grp_id, event.seq)
    if Config.ignore_self and event.uin == client.uin:
        return
    logger.onebot.info(f"Received message ({message_id}/{event.seq}) from group ({event.grp_id}): {event.msg}")
    msg_chain = event.msg_chain
    event_content = event.__dict__
    event_content.pop("msg_chain")
    record_data = MessageEvent(
        msg_id=message_id,
        msg_chain=[segment.__dict__ for segment in (await converter.convert_to_segments(msg_chain, "grp", group_id=event.grp_id))],
        **(event_content)
    )
    db.save(record_data)
    return [
            GroupMessageEvent(
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
    ]

@init_handler
async def GroupDecreaseEventHandler(client: Client, converter: MessageConverter, event: GroupMemberQuit):
    if event.is_kicked_self:
        sub_type = "kick_me"
    elif event.is_kicked and not event.is_kicked_self:
        sub_type = "kick"
    else:
        sub_type = "leave"
    if event.operator_uid == "":
        operator_id = 0
    else:
        correct_operator_uid = "".join(
            [
                char
                for char
                in event.operator_uid.split("\n")[2].split(" ")[0] if char.isprintable()
            ]
        )
        operator_id = get_user_info(correct_operator_uid)
    if operator_id is None:
        operator_id = 0
    return [
        GroupDecreaseNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            sub_type=sub_type,
            group_id=event.grp_id,
            operator_id=int(operator_id),
            user_id=event.uin
        )
    ]

@init_handler
async def GroupRecallEventHandler(client: Client, converter: MessageConverter, event: GroupRecall):
    uin = get_user_info(event.uid)
    if not uin:
        return
    message_event: MessageEvent | Any = db.where_one(MessageEvent(), "seq = ? AND grp_id = ?", event.seq, event.grp_id, default=None)
    if message_event is None:
        return
    return [
        GroupRecallNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            group_id=event.grp_id,
            operator_id=int(uin),
            user_id=message_event.uin,
            message_id=message_event.msg_id
        )
    ]

@init_handler
async def GroupRequestEventHandler(client: Client, converter: MessageConverter, event: GroupInvite | GroupMemberJoinRequest):
    latest_request = (await client.fetch_grp_request()).requests[0]
    if event.invitor_uid is None:
        return
    uin = get_user_info(event.invitor_uid)
    if not uin:
        return
    sub_type = "invite" if isinstance(event, GroupInvite) else "add"
    return [
        GroupRequestEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            sub_type=sub_type,
            group_id=event.grp_id,
            user_id=int(uin),
            comment="" if isinstance(event, GroupInvite) else str(event.answer),
            flag=str(event.grp_id) + "-" + str(latest_request.seq) + "-" + str(latest_request.event_type) + "-" + sub_type
        )
    ]

@init_handler
async def GroupPokeNotifyEventHandler(client: Client, converter: MessageConverter, event: GroupNudge):
    return [
        GroupPokeNotifyNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            group_id=event.grp_id,
            user_id=event.sender_uin,
            target_id=event.target_uin
        )
    ]

@init_handler
async def GroupBanEventHandler(client: Client, converter: MessageConverter, event: GroupMuteMember):
    operator_uid = event.operator_uid
    target_uid = event.target_uid
    operator_uin = get_user_info(operator_uid)
    target_uin = get_user_info(target_uid)
    if operator_uin is None:
        return
    if target_uid != "" and target_uin is None:
        return
    duration = event.duration
    if target_uid == "":
        target_uin = 0
        duration = -1
    return [
        GroupBanNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            group_id=event.grp_id,
            operator_id=int(operator_uin),
            user_id=int(target_uin), # type: ignore
            duration=duration
        )
    ]

@init_handler
async def GroupIncreaseEventHandler(client: Client, converter: MessageConverter, event: GroupMemberJoined | GroupMemberJoinedByInvite):
    # 谁放的？不知道
    if isinstance(event, GroupMemberJoined):
        # 非邀请入群
        formatted_event = GroupIncreaseNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            sub_type="approve",
            group_id=event.grp_id,
            operator_id=0,
            user_id=0,
        )
        # 啥也不知道 暂时先全传0
        # 欲知后事如何，且听`get_group_member_list`分解（
    elif isinstance(event, GroupMemberJoinedByInvite):
        # 邀请入群
        formatted_event = GroupIncreaseNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            sub_type="invite",
            group_id=event.grp_id,
            operator_id=0,
            user_id=event.uin
        )
    return [formatted_event]

@init_handler
async def GroupAdminEventHandler(client: Client, converter: MessageConverter, event: GroupAdminChange):
    uin = get_user_info(event.uid)
    if uin is None:
        return
    return [
        GroupAdminNoticeEvent(
            time=int(datetime.now().timestamp()),
            self_id=client.uin,
            sub_type="set" if event.status else "unset",
            group_id=event.grp_id,
            user_id=uin
        )
    ]