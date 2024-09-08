from typing import Literal
from pydantic import BaseModel

from .ManualEvent import Event, Sender, Anonymous

class GroupMessageSender(Sender):
    card: str = ""
    area: str = ""
    level: str = ""
    role: Literal["owner", "admin", "member"] = "member"
    title: str = ""

class MessageEvent(Event):
    post_type: Literal["message"] = "message"
    message_type: Literal["group", "private"] = "group"
    sub_type: Literal["friend", "group", "other", "normal", "anonymous", "notice"] = "friend"
    message_id: int = 0
    user_id: int = 0
    message: str = ""
    raw_message: str = ""
    font: int = 0
    sender: Sender = Sender()

class GroupDecreaseEvent(Event):
    notice_type: str = "group_decrease"
    sub_type: Literal["leave", "kick", "kick_me"]
    group_id: int = 0
    operator_id: int = 0
    user_id: int = 0

class GroupRecallEvent(Event):
    post_type: str = "notice"
    notice_type: str = "group_recall"
    group_id: int = 0
    user_id: int = 0
    operator_id: int = 0
    message_id: int = 0

class GroupMessageEvent(MessageEvent):
    message_type: Literal["group"] = "group"
    sub_type: Literal["normal", "anonymous", "notice"] = "normal"
    group_id: int = 0
    anonymous: Anonymous = Anonymous()
    sender: GroupMessageSender = GroupMessageSender()

class PrivateMessageEvent(MessageEvent):
    message_type: Literal["private"] = "private"
    sub_type: Literal["friend", "group", "other"] = "friend"