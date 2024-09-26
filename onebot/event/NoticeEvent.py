from typing import Literal

from .ManualEvent import Event

class NoticeEvent(Event):
    post_type: str = "notice"

class GroupDecreaseNoticeEvent(NoticeEvent):
    notice_type: str = "group_decrease"
    sub_type: Literal["leave", "kick", "kick_me"]
    group_id: int = 0
    operator_id: int = 0
    user_id: int = 0

class GroupRecallNoticeEvent(NoticeEvent):
    notice_type: str = "group_recall"
    group_id: int = 0
    user_id: int = 0
    operator_id: int = 0
    message_id: int = 0

class FriendRecallNoticeEvent(NoticeEvent):
    notice_type: str = "friend_recall"
    user_id: int = 0
    message_id: int = 0

class FriendAddNoticeEvent(NoticeEvent):
    notice_type: str = "friend_add"
    user_id: int = 0

class GroupBanNoticeEvent(NoticeEvent):
    notice_type: str = "group_ban"
    group_id: int = 0
    operator_id: int = 0
    user_id: int = 0
    duration: int = 0